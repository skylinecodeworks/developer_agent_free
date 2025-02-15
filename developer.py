#!/usr/bin/env python3
import os
import requests
import docker
import paramiko
import logging
import shlex
import json
from dotenv import load_dotenv
from time import sleep
from github import Github, GithubException
from datetime import datetime

load_dotenv()

# ---------------------------------------------------------
# Configuración (variables de entorno)
# ---------------------------------------------------------
LLM_URL = os.getenv("LLM_URL", "http://localhost:11434/api/generate")
DOCKER_IMAGE = os.getenv("DOCKER_IMAGE", "python:3.10-slim")
SSH_USER = os.getenv("SSH_USER", "devuser")
SSH_PASSWORD = os.getenv("SSH_PASSWORD", "devpass")
SSH_PORT = int(os.getenv("SSH_PORT", 2222))

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_REPO = os.getenv("GITHUB_REPO", "")

# ---------------------------------------------------------
# Logger
# ---------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# Comunicación con el LLM
# ---------------------------------------------------------
def solicitar_codigo_a_llm(instruccion: str) -> str:
    """
    Envía la solicitud a la API del modelo de lenguaje para
    generar/modificar código en Python.
    """
    prompt = (
        "Eres un asistente de desarrollo de software en Python. "
        "Te daré una tarea y tu objetivo es generar o modificar "
        "un bloque de código Python, bien estructurado y documentado, "
        "siguiendo buenas prácticas y proporcionando ejemplos si son relevantes. "
        "Solo responde con el código (sin explicaciones).\n\n"
        f"Solicitud: {instruccion}\n\n"
        "# Responde ÚNICAMENTE con código Python:\n"
    )

    payload = {
        "model": "mistral:latest",  # Ajustar según tu modelo
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(LLM_URL, json=payload)
        response.raise_for_status()
        respuesta_json = response.json()
        return respuesta_json.get("response", "")
    except requests.RequestException as e:
        msg_error = f"Error en la comunicación con el LLM: {e}"
        logger.error(msg_error)
        return ""

# ---------------------------------------------------------
# Manejo del contenedor Docker
# ---------------------------------------------------------
def iniciar_contenedor() -> docker.models.containers.Container:
    """
    Inicia o reutiliza un contenedor Docker con Python y un servidor SSH.
    """
    try:
        client = docker.from_env()
        contenedores = client.containers.list(all=True, filters={"name": "python_sandbox"})
        if contenedores:
            container = contenedores[0]
            if container.status != "running":
                container.start()
                logger.info("Contenedor existente iniciado nuevamente.")
            else:
                logger.info("El contenedor ya está en ejecución.")
            return container

        logger.info(f"Usando imagen: {DOCKER_IMAGE}")
        try:
            client.images.get(DOCKER_IMAGE)
        except docker.errors.ImageNotFound:
            logger.info(f"No se encontró la imagen {DOCKER_IMAGE}. Descargando...")
            client.images.pull(DOCKER_IMAGE)

        container = client.containers.run(
            DOCKER_IMAGE,
            name="python_sandbox",
            detach=True,
            tty=True,
            stdin_open=True,
            ports={"22/tcp": SSH_PORT},
            restart_policy={"Name": "always"},
            command=(
                "/bin/sh -c '"
                "apt-get update && apt-get install -y openssh-server git && "
                f"useradd -m -s /bin/bash {SSH_USER} && "
                f"echo \"{SSH_USER}:{SSH_PASSWORD}\" | chpasswd && "
                "mkdir -p /run/sshd && "
                "sed -i \"s/.*Port 22/Port 22/g\" /etc/ssh/sshd_config && "
                "sed -i \"s/.*PasswordAuthentication no/PasswordAuthentication yes/g\" /etc/ssh/sshd_config && "
                "echo \"PermitRootLogin yes\" >> /etc/ssh/sshd_config && "
                "service ssh start && "
                "while true; do sleep 300; done'"
            )
        )
        logger.info("Esperando que el servicio SSH arranque dentro del contenedor...")
        sleep(5)
        container.reload()
        logger.info(f"Contenedor {container.id} iniciado con SSH en el puerto {SSH_PORT}.")
        return container
    except Exception as e:
        msg_error = f"Error iniciando el contenedor Docker: {e}"
        logger.error(msg_error)
        raise RuntimeError(msg_error)

def obtener_ip_contenedor(_: docker.models.containers.Container) -> str:
    """
    Retorna la IP del contenedor. Con mapeo de puertos locales,
    podemos usar 127.0.0.1.
    """
    return "127.0.0.1"

# ---------------------------------------------------------
# SSH dentro del contenedor
# ---------------------------------------------------------
def ejecutar_comando_ssh(container_ip: str, comando: str):
    """
    Ejecuta un comando en el contenedor vía SSH y retorna la salida y errores.
    """
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=container_ip,
            port=SSH_PORT,
            username=SSH_USER,
            password=SSH_PASSWORD,
            allow_agent=False,
            look_for_keys=False,
        )
        stdin, stdout, stderr = ssh.exec_command(comando)
        salida = stdout.read().decode("utf-8")
        errores = stderr.read().decode("utf-8")
        ssh.close()
        return salida, errores
    except Exception as e:
        msg_error = f"Error ejecutando comando vía SSH: {e}"
        logger.error(msg_error)
        raise RuntimeError(msg_error)

# ---------------------------------------------------------
# Funciones para integración con GitHub
# ---------------------------------------------------------
def commit_and_create_pr(
    file_path: str,
    new_content: str,
    commit_message: str,
    title_pr: str,
    body_pr: str
) -> None:
    """
    1. Crea una rama de feature basada en la rama principal (default_branch).
    2. Crea o actualiza el archivo `file_path` con `new_content` en la nueva rama.
    3. Crea un Pull Request desde la nueva rama a la rama principal.
    """
    if not GITHUB_TOKEN or not GITHUB_REPO:
        logger.error("No se ha configurado el GITHUB_TOKEN o GITHUB_REPO.")
        return

    try:
        # Autenticación e identificación del repositorio
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(GITHUB_REPO)

        # Obtenemos la rama principal
        main_branch = repo.get_branch(repo.default_branch)
        base_sha = main_branch.commit.sha

        # Creamos una rama nueva (ej: feature-YYYYmmddHHMM)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        feature_branch_name = f"feature-{timestamp}"
        ref_new_branch = f"refs/heads/{feature_branch_name}"

        logger.info(f"Creando rama: {feature_branch_name} a partir de {repo.default_branch}")
        repo.create_git_ref(ref=ref_new_branch, sha=base_sha)

        # Verificar si el archivo existe o no
        try:
            contents = repo.get_contents(file_path, ref=repo.default_branch)
            # Si existe, actualizamos
            logger.info(f"Archivo {file_path} existe. Se actualizará en la nueva rama.")
            repo.update_file(
                path=contents.path,
                message=commit_message,
                content=new_content,
                sha=contents.sha,
                branch=feature_branch_name
            )
        except GithubException as e:
            if e.status == 404:
                # Si no existe, lo creamos
                logger.info(f"Archivo {file_path} no existe. Se creará en la nueva rama.")
                repo.create_file(
                    path=file_path,
                    message=commit_message,
                    content=new_content,
                    branch=feature_branch_name
                )
            else:
                logger.error(f"Error consultando el archivo en GitHub: {e}")
                raise

        # Crear el Pull Request
        pr = repo.create_pull(
            title=title_pr,
            body=body_pr,
            head=feature_branch_name,
            base=repo.default_branch
        )
        logger.info(f"Pull Request creado: {pr.html_url}")

    except Exception as e:
        logger.error(f"Error al crear rama y/o PR: {e}")

# ---------------------------------------------------------
# Función principal
# ---------------------------------------------------------
def main():
    container = iniciar_contenedor()
    container_ip = obtener_ip_contenedor(container)

    while True:
        instruccion = input("\nDescribe la tarea (o 'salir' para terminar): ")
        if instruccion.lower() == "salir":
            logger.info("Saliendo del programa.")
            break

        # 1️⃣ Solicitar código al LLM
        codigo_generado = solicitar_codigo_a_llm(instruccion)
        if not codigo_generado.strip():
            logger.warning("El LLM no devolvió una propuesta válida.")
            continue

        # 2️⃣ Limpiar caracteres de Markdown
        codigo_generado = codigo_generado.strip("`").replace("```python", "").replace("```", "").strip()

        # Eliminar "python" si aparece como primera línea
        if codigo_generado.startswith("python"):
            codigo_generado = "\n".join(codigo_generado.split("\n")[1:]).strip()


        print("\nCódigo propuesto:\n")
        print(codigo_generado)

        # 3️⃣ Confirmación del usuario
        opcion = input("\n¿Deseas validar/ejecutar el código en el contenedor? (s/n): ")
        if opcion.lower() == "s":
            file_name = "main.py"

            # Guardar código en el contenedor
            echo_comando = f'cat <<EOF > {file_name}\n{codigo_generado}\nEOF'


            ejecutar_comando_ssh(container_ip, echo_comando)

            # 4️⃣ Instalar dependencias correctamente
            instalar_deps = (
                "pip install --no-cache-dir --break-system-packages pytest black && "
                "ln -s $(python3 -m site --user-base)/bin/black /usr/local/bin/black && "
                "ln -s $(python3 -m site --user-base)/bin/pytest /usr/local/bin/pytest"
            )
            salida, errores = ejecutar_comando_ssh(container_ip, instalar_deps)
            print("\n--- Instalación de dependencias ---")
            print(salida)
            if errores:
                print("Errores durante la instalación:", errores)

            # 5️⃣ Verificar que `black` y `pytest` están instalados
            verificar_instalacion = "export PATH=$HOME/.local/bin:$PATH && which black && which pytest"

            salida, errores = ejecutar_comando_ssh(container_ip, verificar_instalacion)

            if not salida.strip():
                print("\n⚠️ Error: `black` y/o `pytest` no se encuentran en el contenedor.")
                print("Intenta instalar manualmente ejecutando en el contenedor:")
                print("pip install --no-cache-dir pytest black --break-system-packages")
                return

            # 6️⃣ Ejecutar linting con Black
            lint_comando = f"export PATH=$HOME/.local/bin:$PATH && black --check {file_name}"
            lint_out, lint_err = ejecutar_comando_ssh(container_ip, lint_comando)
            print("\n--- Linting (Black) ---")
            print(lint_out or "")
            print(lint_err or "")

            # 7️⃣ Ejecutar pruebas con pytest
            test_comando = f"export PATH=$HOME/.local/bin:$PATH && pytest {file_name}"
            test_out, test_err = ejecutar_comando_ssh(container_ip, test_comando)
            print("\n--- Testing (pytest) ---")
            print(test_out or "")
            print(test_err or "")

            # 8️⃣ Finalmente, ejecutar el código
            run_comando = f"python {file_name}"
            salida, errores = ejecutar_comando_ssh(container_ip, run_comando)
            print("\n--- Salida de la ejecución ---")
            print(salida)
            if errores:
                print("\n--- Errores ---")
                print(errores)
            else:
                # ✅ 8️⃣ Si todo funciona, hacer commit y crear PR
                commit_message = "feat: Agrega funcionalidad de suma automática"
                title_pr = "Nueva funcionalidad: Suma de enteros"
                body_pr = "Este Pull Request agrega la funcionalidad solicitada para sumar enteros."

                commit_and_create_pr(
                    file_path=file_name,
                    new_content=codigo_generado,
                    commit_message=commit_message,
                    title_pr=title_pr,
                    body_pr=body_pr
                )

if __name__ == "__main__":
    main()

