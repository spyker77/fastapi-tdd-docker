# Pull official base image
FROM python:3.11-slim-buster

# Set working directory
WORKDIR /code

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:$PATH"

# Create the app user
RUN addgroup --system app && \
    adduser --system --group app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential netcat libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY poetry.lock pyproject.toml ./
RUN pip install --upgrade pip && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    poetry export -f requirements.txt --output requirements.txt --with dev --without-hashes && \
    pip install -r requirements.txt

# Add app and chown all the files to the app user
COPY --chown=app:app . .

# Change to the app user
USER app
