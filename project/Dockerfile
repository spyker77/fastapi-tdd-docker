# Pull official base image
FROM python:3.8.7-slim-buster

# Set working directory
WORKDIR /usr/src/app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y \
    netcat gcc postgresql \
    # Dependencies for newspaper3k
    libxml2-dev libxslt-dev libjpeg-dev zlib1g-dev libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
COPY requirements-dev.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements-dev.txt

# Add the app
COPY . .

# Add entrypoint.sh
COPY entrypoint.sh .
RUN chmod +x /usr/src/app/entrypoint.sh

# Run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]