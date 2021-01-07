# pull official base image
FROM python:3.9-slim-buster

# set working directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# install system dependencies
RUN apt-get update \
    && apt-get install -y netcat gcc postgresql \
    && rm -rf /var/lib/apt/lists/*

# install python dependencies
COPY ./requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# add app
COPY . .

# add entrypoint.sh
COPY ./entrypoint.sh .
RUN chmod +x /usr/src/app/entrypoint.sh

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]