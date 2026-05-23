# syntax=docker/dockerfile:1.7

# Use an official Python runtime as a parent image
FROM python:3.14-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required at runtime
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl postgresql-client \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=0

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install dependencies with cached pip downloads
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Copy the rest of the application's code to the working directory
# In development, this is mounted as a volume for hot reload
COPY . .

# Copy and set permissions for entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set environment variables for the database connection
ENV POSTGRES_USER=user
ENV POSTGRES_PASSWORD=password
ENV POSTGRES_DB=serviperfiles_db
ENV DATABASE_URL=postgresql://user:password@db:5432/serviperfiles_db

# Expose port 8000 to the outside world
EXPOSE 8000

# Use entrypoint script that runs migrations before starting the app
ENTRYPOINT ["/entrypoint.sh"]
