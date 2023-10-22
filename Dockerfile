###########
# BUILDER #
###########

# Pull official base image
FROM python:3.11-slim-buster as builder

# Set work directory
WORKDIR /code

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:$PATH"

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY poetry.lock pyproject.toml ./
RUN pip install --upgrade pip && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    poetry export -f requirements.txt --output requirements.txt --without-hashes && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /code/wheels -r requirements.txt


#########
# FINAL #
#########

# Pull official base image
FROM python:3.11-slim-buster

# Set working directory
WORKDIR /home/app

# Set environment variables
ENV ENVIRONMENT=dev \
    TESTING=0

# Create the app user and install system dependencies
RUN addgroup --system app && \
    adduser --system --group app && \
    apt-get update && \
    apt-get install -y --no-install-recommends netcat libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY --from=builder /code/wheels /wheels
COPY --from=builder /code/requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir /wheels/*

# Add app and chown all the files to the app user
COPY --chown=app:app . .

# Change to the app user
USER app
