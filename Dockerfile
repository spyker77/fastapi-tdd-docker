#####################
# 1 STAGE - BUILDER #
#####################

# Pull official Python image
FROM python:3.11.6-slim AS builder

# Set work directory
WORKDIR /code

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && \
    pip install --upgrade pip pdm && \
    rm -rf /var/lib/apt/lists/*

# Copy PDM files and install python dependencies
COPY pyproject.toml pdm.lock README.md ./
RUN mkdir __pypackages__ && pdm sync --dev

###################
# 2 STAGE - FINAL #
###################

# Pull NVIDIA CUDA runtime image
FROM nvidia/cuda:12.2.2-cudnn8-runtime-ubuntu22.04 AS final

# Set work directory
WORKDIR /home/app

# Set environment variables
ENV ENVIRONMENT=dev \
    TESTING=0 \
    PYTHONPATH=/home/pkgs \
    DEBIAN_FRONTEND=noninteractive \
    LD_LIBRARY_PATH=/usr/local/cuda/lib64:${LD_LIBRARY_PATH}

# Create the app user and install system dependencies
RUN addgroup --system app && \
    adduser --system --group app && \
    apt-get update && \
    apt-get install -y --no-install-recommends software-properties-common && \
    # Add the deadsnakes PPA for Python 3.11
    add-apt-repository ppa:deadsnakes/ppa && \
    # Add repos where to find the libcupti12 for CUDA
    add-apt-repository "deb http://archive.ubuntu.com/ubuntu/ mantic main multiverse" && \
    apt-get update && \
    apt-get install -y python3.11 libcupti12=12.0.* && \
    # Create a symlink for Python
    ln -s /usr/bin/python3.11 /usr/local/bin/python && \
    rm -rf /var/lib/apt/lists/*

# Copy packages and executables from the builder stage
COPY --from=builder /code/__pypackages__/3.11/lib /home/pkgs
COPY --from=builder /code/__pypackages__/3.11/bin/* /usr/local/bin/

# Add app and chown all the files to the app user
COPY --chown=app:app . .

# Change to the app user
USER app
