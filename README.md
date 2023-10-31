# Test-Driven Development with FastAPI and Docker

![Continuous Integration and Delivery](https://github.com/spyker77/fastapi-tdd-docker/workflows/Continuous%20Integration%20and%20Delivery/badge.svg?branch=main)

This is the implementation of [the course](https://testdriven.io/courses/tdd-fastapi/) with the following changes so far:

- Dependencies updated to the latest version at the moment
- CORSMiddleware used to manually control allowed origins
- Venv replaced with PDM
- Added versions of the API
- Refactored the code
- Gunicorn added to manage the uvicorn
- BackgroundTasks replaced with Celery, Redis and RabbitMQ
- Optimized CI/CD pipeline in GitHub Actions
- Migrated to the Container registry from the Docker registry
- Implemented authentication and authorization using OAuth2
- Tortoise-ORM has been replaced by SQLAlchemy
- Transformers model is used instead of NLP from Newspaper3k

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

Tests can be run with this command:

```bash
docker compose exec web pytest -n auto --cov
```

## Note

Current implementation of text summarization using the transformer model is not ideal for production:

- The need to install a heavy transformers library with its dependencies;
- The need to download several gigs of the model;
- The need for powerful hardware to run it.

Typically, the model is provided via API using services like AWS SageMaker or Paperspace Gradient.
