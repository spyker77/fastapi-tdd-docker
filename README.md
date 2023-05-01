# Test-Driven Development with FastAPI and Docker

![Continuous Integration and Delivery](https://github.com/spyker77/fastapi-tdd-docker/workflows/Continuous%20Integration%20and%20Delivery/badge.svg?branch=main)

This is the implementation of [the course](https://testdriven.io/courses/tdd-fastapi/) with the following changes so far:

- Python image updated to the latest version 3.11
- Dependencies updated to the latest version at the moment
- CORSMiddleware used to manually control allowed origins
- Venv replaced with poetry
- Added versions of the API
- Refactored the code
- Gunicorn added to manage the uvicorn
- BackgroundTasks replaced with Celery, Redis and RabbitMQ
- Optimized CI/CD pipeline in GitHub Actions
- Migrated to the Container registry from the Docker registry
- Implemented authentication and authorization using OAuth2
- Tortoise-ORM has been replaced by SQLAlchemy

## Quick Start

Spin up the containers:

```bash
docker compose up -d --build
```

Generate the database schema on first launch:

```bash
docker compose exec web alembic upgrade head
```

Open in your browser: <http://localhost:8000/docs>
