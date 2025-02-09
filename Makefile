.PHONY: setup run clean setup-db migrate reset-db lint
.PHONY: docker-build docker-run docker-stop docker-rebuild docker-logs

# DOCKER
# Build the Docker image with the name "timetraveler"
docker-build:
	docker build -t timetraveler .

# Run the Docker container in detached mode, mapping host port 80 to container port 5000, then open the browser at http://localhost
docker-run:
	docker run -d --name timetraveler -p 80:5000 timetraveler
	@sleep 2  # Wait a moment for the container to start
	open http://localhost

# Stop and remove the Docker container if it is running
docker-stop:
	docker stop timetraveler || true
	docker rm timetraveler || true

# Rebuild the image and run the container (stopping any existing container first)
docker-rebuild: docker-stop docker-build docker-run

# Tail the logs of the running Docker container
docker-logs:
	docker logs -f timetraveler


# Define DB_* variables by extracting them from your Python settings.
# With the updated settings, these commands should only output the desired values.
DB_USER := $(shell poetry run python -c "from core.config import settings; print(settings.DB_USER)")
DB_HOST := $(shell poetry run python -c "from core.config import settings; print(settings.DB_HOST)")
DB_PORT := $(shell poetry run python -c "from core.config import settings; print(settings.DB_PORT)")
DB_NAME := $(shell poetry run python -c "from core.config import settings; print(settings.DB_NAME)")

# Set up the environment and install dependencies using Poetry
setup:
	poetry install
	poetry run python scripts/setup_db.py

# Run the journey cron script in debug mode
run:
	poetry run python -m scripts.journey_cron --debug

# Clean up the environment
clean:
	rm -rf $(shell poetry env info --path)

# Initialize the database without dropping it
setup-db:
	poetry run python scripts/setup_db.py

# Apply Alembic migrations
migrate:
	poetry run alembic upgrade head

# Drop and recreate the database, then apply migrations
reset-db:
	psql -U $(DB_USER) -h $(DB_HOST) -p $(DB_PORT) -d postgres -c "DROP DATABASE IF EXISTS $(DB_NAME);"
	poetry run python scripts/setup_db.py

# Chain linters
lint:
	poetry run flake8 .
	poetry run black .
	poetry run isort .
	poetry run mypy .
