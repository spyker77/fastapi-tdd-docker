# Pull official base image
FROM python:3.9-slim-buster

# Set working directory
WORKDIR /code

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

# Add entrypoint.sh
COPY ./entrypoint.sh .
RUN chmod +x /code/entrypoint.sh

# Run entrypoint.sh
ENTRYPOINT ["/code/entrypoint.sh"]