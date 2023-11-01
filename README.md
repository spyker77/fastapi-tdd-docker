# Test-Driven Development with FastAPI and Docker

![Continuous Integration and Delivery](https://github.com/spyker77/fastapi-tdd-docker/workflows/Continuous%20Integration%20and%20Delivery/badge.svg?branch=main)

## Table of Contents

- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [Deployment](#deployment)
- [License](#license)

## Introduction

This project is an implementation of [the course](https://testdriven.io/courses/tdd-fastapi/) on Test-Driven Development to build the API for summarizing articles, with additional features and optimizations. Key enhancements include:

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

## Prerequisites

- Docker and Docker Compose installed on your machine.
- Basic knowledge of Python, FastAPI, and Docker.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/spyker77/fastapi-tdd-docker.git
cd fastapi-tdd-docker
```

2. Build and start the containers:

```bash
docker compose up -d --build
```

3. Generate the database schema:

```bash
docker compose exec web alembic upgrade head
```

## Usage

1. Access the API documentation at: <http://localhost:8000/docs>
2. Create a test user at: <http://localhost:8000/docs#/users/create_user_api_v2_users__post>

    Example of the payload:

```json
{
  "full_name": "Cute Koala",
  "username": "cute",
  "email": "cute@example.com",
  "password": "supersecret"
}
```

3. Use the **Authorize** button (simplest way) at the top and enter the username and password you've just created, then click **Authorize**.

4. At this point you're authorized. Now use the endpoint <http://localhost:8000/docs#/summaries/create_summary_api_v2_summaries__post> to send the article you want to summarize, for example like so:

```json
{
  "url": "https://dev.to/spyker77/how-to-connect-godaddy-domain-with-heroku-and-cloudflare-mdh"
}
```

5. This triggers the ML model to download, which may take a few minutes for the first run (in the current implementation). After that, reach the endpoint <http://localhost:8000/docs#/summaries/read_all_summaries_api_v2_summaries__get> and in the response you should see something like:

```json
[
  {
    "id": 1,
    "url": "https://dev.to/spyker77/how-to-connect-godaddy-domain-with-heroku-and-cloudflare-mdh",
    "summary": "If you struggle to connect newly registered domain from GoDaddy with your app at Heroku, and in addition would like to use advantages of Cloudflare – this article is for you. Hope it will help you and without many words, let's jump in!Sections: Heroku settings, Cloudflare settings and GoDaddy settings.",
    "user_id": 1
  }
]
```

## Testing

Run the tests using the following command:

```bash
docker compose exec web pytest -n auto --cov
```

## Deployment

For production deployment, don't forget to change the ENVIRONMENT variables. The default CI/CD pipeline is set up to build images with GitHub Actions, store them in GitHub Packages, and deploy the application to Heroku. But the deployment part is currently disabled/commented out.

### Note

The current implementation of text summarization using the transformer model is not ideal for production due to the following reasons:

- The requirement to install a heavy transformers library along with its dependencies.
- The necessity to download several gigabytes of the model.
- The need for powerful hardware to run the model.

Typically, in a production environment, the model would be provided via an API using services like AWS SageMaker or Paperspace Gradient.

## License

This project is licensed under the MIT License. See the [MIT License](LICENSE) file for details.
