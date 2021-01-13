# Test-Driven Development with FastAPI and Docker

![Continuous Integration and Delivery](https://github.com/spyker77/fastapi-tdd-docker/workflows/Continuous%20Integration%20and%20Delivery/badge.svg?branch=main)

This is the implementation of [the course](https://testdriven.io/courses/tdd-fastapi/) with the following changes so far: 

-   Python image updated to the latest version 3.9
-   Dependencies updated to the latest version at the moment
-   Migrations added via Aerich from Tortoise-ORM
-   CORSMiddleware used to manually control allowed origins
-   Added a handler for the error caused by forced SSL connection in PostgreSQL with Heroku
-   Changed database test url to use the same url everywhere due to overly complex configuration (or related error otherwise)
