# Test-Driven Development with FastAPI and Docker

![Continuous Integration and Delivery](https://github.com/spyker77/fastapi-tdd-docker/workflows/Continuous%20Integration%20and%20Delivery/badge.svg?branch=main)

This is the implementation of [the course](https://testdriven.io/courses/tdd-fastapi/) with the following changes so far: 

-   Python image updated to the latest version 3.9
-   Dependencies updated to the latest version at the moment
-   Migrations added via Aerich from Tortoise-ORM
-   CORSMiddleware used to manually control allowed origins
-   Venv replaced with poetry
-   Added versions of the API
-   Refactored the code
-   Test coverage increased from 86 to 94%
-   Gunicorn added to manage the uvicorn
-   BackgroundTasks replaced witn Celery, Redis and RabbitMQ
