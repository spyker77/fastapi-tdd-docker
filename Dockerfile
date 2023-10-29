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

# COPY PDM files and install python dependencies
COPY pyproject.toml pdm.lock README.md ./
RUN mkdir __pypackages__ && pdm sync --dev

########################
# 2 STAGE - CUDA-DEVEL #
########################

# Pull NVIDIA CUDA devel image
FROM nvidia/cuda:12.2.2-cudnn8-devel-ubuntu22.04 AS cuda_devel

# Locate libcupti.so.12 and copy it to a known location
RUN find /usr/local/cuda/lib64 -name 'libcupti.so.12' -exec cp {} /usr/local/cuda/lib64/libcupti.so.12 \;

###################
# 3 STAGE - FINAL #
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

# Create the app user and install system dependencies including Python
RUN addgroup --system app && \
    adduser --system --group app && \
    apt-get update && \
    apt-get install -y --no-install-recommends software-properties-common && \
    # Add the deadsnakes PPA to get Python 3.11
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.11 && \
    # Create a symlink for Python
    ln -s /usr/bin/python3.11 /usr/local/bin/python && \
    rm -rf /var/lib/apt/lists/* 

# Copy libcupti.so.12 from the devel stage to the runtime stage
COPY --from=cuda_devel /usr/local/cuda/lib64/libcupti.so.12 /usr/local/cuda/lib64/libcupti.so.12

# Copy packages and executables from the builder stage
COPY --from=builder /code/__pypackages__/3.11/lib /home/pkgs
COPY --from=builder /code/__pypackages__/3.11/bin/* /usr/local/bin/

# Add app and chown all the files to the app user
COPY --chown=app:app . .

# Change to the app user
USER app
