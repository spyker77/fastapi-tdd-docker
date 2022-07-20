# Pull official base image
FROM python:3.10-slim-buster


# Create the app user
RUN addgroup --system app \
    && adduser --system --group app

# Set working directory
WORKDIR /code

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    netcat \
    postgresql \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY poetry.lock .
COPY pyproject.toml .
RUN pip install --upgrade pip \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && export PATH="/root/.local/bin:$PATH" \
    && poetry export -f requirements.txt --output requirements.txt --dev --without-hashes \
    && pip install -r requirements.txt

# Add app
COPY . .

# Chown all the files to the app user
RUN chown -R app:app /code

# Change to the app user
USER app