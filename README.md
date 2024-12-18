
# Project API Docker Setup

This project provides an API for managing projects, employees, and their allocations. It supports operations such as CRUD for projects and employees, allocation suggestions, and exporting reports.

## Overview

The API allows:

- **Managing Projects**: Create, update, retrieve, and delete projects.
- **Managing Employees**: Add, update, retrieve, and delete employee records.
- **Allocations**: Suggest best allocation strategies, track current employee/project allocations, and manage employee assignments to projects.
- **Reports**: Export employee allocation reports.

This project is containerized using Docker for easy deployment.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [How to Build the Docker Image](#how-to-build-the-docker-image)
3. [How to Run the Docker Image](#how-to-run-the-docker-image)
4. [How to Pull the Docker Image](#how-to-pull-the-docker-image)
5. [Implementation Choices](#implementation-choices)
6. [Environment Variables](#environment-variables)

---

## Prerequisites

Before you begin, ensure that you have the following:

1. **Docker**: Install Docker on your machine. Follow the [Docker installation guide](https://docs.docker.com/get-docker/).
---

## How to Build the Docker Image

To build the Docker image locally, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/project-api.git
   cd project-api
   ```

2. Build the Docker image using the following command:

   ```bash
   docker build -t your-username/project-api .
   ```

   - This command will use the `Dockerfile` in the current directory to build the image.

---

## How to Run the Docker Image

After the image has been built, you can run it with the following command:

```bash
docker compose up
```

- `-d`: Run the container in detached mode (in the background).
- `-p 8000:8000`: Bind port 8000 of the container to port 8000 on your host machine, so you can access the API at `http://localhost:8000`.

---

## How to Pull the Docker Image

If you prefer to pull the pre-built Docker image from Docker Hub, use the following command:

```bash
docker pull fathieldeabas/ark-web
```


- Once the image is pulled, you can run it as shown in the "How to Run the Docker Image" section.

---

## Implementation Choices

### 1. **Dockerization**

- **Base Image**: The Docker image uses the official Python base image to ensure compatibility and flexibility with Python dependencies.
- **Dockerfile**: The `Dockerfile` contains steps to install necessary dependencies and run the API in a containerized environment.
- **Environment Variables**: Environment variables like database credentials and API keys are handled via Docker environment variables, which can be configured during runtime.

### 2. **API Framework**

- **Django & Django Rest Framework**: The API is built using Django for project structure and management. Django Rest Framework (DRF) is used to build the RESTful API endpoints efficiently.
- **OpenAPI Documentation**: The OpenAPI 3.0 documentation is automatically generated to describe the API endpoints and their responses.

### 3. **Database**

- The project uses a relational database (e.g., PostgreSQL or SQLite) for storing project, employee, and allocation data. Ensure that the necessary environment variables for database connections are configured in the Docker container.

### 4. **Background Tasks**

- **Celery** is used for managing background tasks, such as generating and exporting reports. It ensures that the API remains responsive while handling resource-intensive operations asynchronously.
---

## Environment Variables

When running the Docker container, you may need to specify environment variables such as database credentials or secret keys. You can provide these during the container startup using the `-e` flag or in a `.env` file.

Example of environment variables:

    REDIS_URL=redis://localhost:6379/0
    STATIC_ROOT=/app/staticfiles/static/
    =/app/mediafiles/media
    MKDOCS_ROOT=/app/mediafiles/mkdocs/build

    MKDOCS_KSA_ROOT= /app/mediafiles/mkdocs/build_ksa
    DOCS_STATIC_ROOT=/app/mediafiles/mkdocs/


 you can create a `.env` file and place it in the same directory as your `Dockerfile`. Docker will automatically read this file.

---

## Troubleshooting

- **Port Conflicts**: If port 8000 is already in use, change the port mapping using `-p <host_port>:8000`.
- **Missing Dependencies**: If you're encountering issues with dependencies, ensure you have the correct Python version and that `requirements.txt` is up to date.

---