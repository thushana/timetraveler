# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.6.1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies and Poetry
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Copy the pyproject.toml and poetry.lock files into the container
COPY pyproject.toml poetry.lock ./

# Install Python dependencies
RUN poetry install --no-root --no-dev

# Copy the rest of the application code into the container
COPY . .

# Expose the port your application runs on
EXPOSE 5000

# Command to run your application (adjust as needed)
CMD ["python", "scripts/journey_cron.py"]
