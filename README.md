```markdown
# Skyline Codeworks - AI Code Generator & Docker Runner

This project is a Python-based tool designed to automate code generation, testing, and deployment in a secure and efficient way. It integrates a local language model (LLM) API to generate Python code on demand, runs that code inside a Docker container via SSH, and even automates GitHub commits and pull requests for continuous integration.

---

# Skyline Codeworks - Generador de Código con IA y Ejecución en Docker

Este proyecto es una herramienta en Python que automatiza la generación, prueba y despliegue de código de forma segura y eficiente. Integra una API de modelo de lenguaje local (LLM) para generar código Python a pedido, ejecuta ese código dentro de un contenedor Docker mediante SSH y automatiza commits y pull requests en GitHub para lograr una integración continua.

---

## Features / Funcionalidades

- **Dynamic Code Generation / Generación Dinámica de Código:**  
  Utiliza un LLM local para generar código Python basado en las instrucciones del usuario.

- **Docker Integration / Integración con Docker:**  
  Ejecuta el código generado en un contenedor Docker seguro, garantizando un entorno consistente y aislado.

- **SSH Command Execution / Ejecución de Comandos vía SSH:**  
  Conecta al contenedor usando SSH para ejecutar comandos de instalación, linting y pruebas.

- **Automated Quality Checks / Verificación Automática de Calidad:**  
  Emplea herramientas como Black para formateo y pytest para pruebas, asegurando que el código cumpla con altos estándares.

- **GitHub Automation / Automatización en GitHub:**  
  Facilita la integración continua mediante la creación de commits y pull requests directamente desde el script.

---

## Requirements / Requisitos

- **Python 3.10+**
- **Docker:** Asegúrate de tener Docker instalado y en funcionamiento.
- **SSH Client (via paramiko):** Para la ejecución de comandos dentro del contenedor.
- **Local LLM API:** Un servicio local que responda en la URL definida por `LLM_URL`.
- **GitHub Account & Token:** Para la integración con GitHub (definir en `GITHUB_TOKEN` y `GITHUB_REPO`).

---

## Setup & Installation / Configuración e Instalación

1. **Clone the Repository / Clona el Repositorio:**
   ```bash
   git clone https://github.com/tu_usuario/tu_repositorio.git
   cd tu_repositorio
   ```

2. **Install Dependencies / Instalar Dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables / Variables de Entorno:**

   Create a `.env` file in the project root and configure the following variables:

   - `LLM_URL`: URL for the local language model API (por ejemplo, `http://localhost:11434/api/generate`).
   - `DOCKER_IMAGE`: Docker image to use (default: `python:3.10-slim`).
   - `SSH_USER`: Username for SSH connections (por ejemplo, `devuser`).
   - `SSH_PASSWORD`: Password for SSH connections (por ejemplo, `devpass`).
   - `SSH_PORT`: Port for SSH (default: `2222`).
   - `GITHUB_TOKEN`: Your GitHub token for authentication.
   - `GITHUB_REPO`: GitHub repository (format: `username/repo`).

---

## Usage / Uso

Run the main script:
```bash
python developer.py
```

The tool will prompt you to:
1. Describe the coding task.
2. Generate code using the LLM API.
3. Test and execute the code inside a secure Docker container.
4. Optionally, commit the code and create a pull request in GitHub.

El programa te guiará para:
1. Describir la tarea de codificación.
2. Generar código mediante la API del LLM.
3. Probar y ejecutar el código en un contenedor Docker seguro.
4. Opcionalmente, hacer commit y crear un pull request en GitHub.

---

## Contributing / Contribuciones

Contributions, bug reports, and feature requests are welcome! Feel free to open an issue or submit a pull request.

¡Se agradecen contribuciones, reportes de errores y solicitudes de nuevas funcionalidades! No dudes en abrir un issue o enviar un pull request.

---

## License / Licencia

This project is licensed under the [MIT License](LICENSE).

Este proyecto está bajo la [Licencia MIT](LICENSE).

---

## Contact / Contacto

For questions or suggestions, feel free to reach out via the GitHub repository or contact the Skyline Codeworks team (tom@skylinecodew.com)

Para preguntas o sugerencias, puedes contactar a través del repositorio de GitHub o comunicarte con el equipo de Skyline Codeworks. (tom@skylinecodew.com)
```
