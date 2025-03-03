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
# Skyline Codeworks - AI Code Generator & Docker Runner with Astral UV

This project is a Python-based tool designed to automate code generation, testing, and deployment in a secure and efficient way. It uses Astral UV for project management and dependency handling, integrates a local language model (LLM) API to generate Python code on demand, runs that code inside a Docker container via SSH, and automates GitHub commits and pull requests for continuous integration.

---

## Features

- **Dynamic Code Generation:**
  Utilizes a local LLM to generate Python code based on user input.

- **Docker Integration:**
  Runs the generated code in a secure Docker container, ensuring a consistent and isolated environment.

- **SSH Command Execution:**
  Connects to the container using SSH to execute installation, linting, and testing commands.

- **Automated Quality Checks:**
  Uses tools like Ruff for formatting and pytest for testing, ensuring high code quality standards.

- **GitHub Automation:**
  Supports continuous integration by automating commits and pull requests directly from the script.

---

## Requirements

- **Python 3.10+**
- **Docker:** Ensure Docker is installed and running.
- **SSH Client (via paramiko):** For command execution within the container.
- **Local LLM API:** A local service responding to the URL defined by `LLM_URL`.
- **GitHub Account & Token:** For integration with GitHub (set in `GITHUB_TOKEN` and `GITHUB_REPO`).

---

## Setup & Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/skylinecodeworks/developer_agent_free
   cd developer_agent_free
   ```

2. **Install Astral UV:**
   ```bash
   pip install astral-uv
   ```

3. **Initialize the Project with Astral UV:**
   ```bash
   uv init
   ```

   This will generate a `pyproject.toml` file with the basic project configuration.

4. **Add Dependencies using Astral UV:**
   ```bash
   uv add paramiko docker requests
   ```

5. **Configure Environment Variables:**
   Create a `.env` file in the project root and set the following variables:

   ```env
   LLM_URL=http://localhost:11434/api/generate
   DOCKER_IMAGE=python:3.10-slim
   SSH_USER=devuser
   SSH_PASSWORD=devpass
   SSH_PORT=2222
   GITHUB_TOKEN=your_github_token
   GITHUB_REPO=username/repo
   ```

---

## Usage

Run the main script:
```bash
uv run main.py
```

The tool will guide you to:
1. Describe the coding task.
2. Generate code using the LLM API.
3. Test and execute the code inside a secure Docker container.
4. Optionally, commit the code and create a pull request in GitHub.

---

## Development Workflow

- **Adding Dependencies:**
  To add a new dependency, use:
  ```bash
  uv add <package_name>
  ```

- **Running Tests:**
  ```bash
  uv test
  ```

- **Linting Code:**
  ```bash
  uv lint
  ```

---

## Contributing

Contributions, bug reports, and feature requests are welcome! Feel free to open an issue or submit a pull request.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Contact

For questions or suggestions, reach out via the GitHub repository or contact the Skyline Codeworks team at (tom@skylinecodew.com).

---

For more information on using Astral UV for Python project management, refer to the [official documentation](https://docs.astral.sh/uv/).


