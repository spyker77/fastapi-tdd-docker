# Pull official base image
FROM python:3.9-slim-buster

# Set working directory
WORKDIR /code

# Create the app user
RUN addgroup --system app \
    && adduser --system --group app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update \
    && apt-get -y install netcat gcc postgresql \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY ./pyproject.toml .
RUN pip install --upgrade pip \
    && pip install poetry \
    && poetry export -f requirements.txt --output requirements.txt --dev \
    && pip install -r requirements.txt

# Add app
COPY . .

# Chown all the files to the app user
RUN chown -R app:app /code

# Change to the app user
USER app

# Run entrypoint.sh
ENTRYPOINT ["/code/entrypoint.sh"]