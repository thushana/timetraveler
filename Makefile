.PHONY: setup run clean database-setup database-migrate database-reset lint
.PHONY: docker-build docker-run docker-stop docker-rebuild docker-logs heroku-config

# DOCKER
# Build the Docker image with the name "timetraveler"
docker-build:
	docker build -t timetraveler .

# Run the Docker container in detached mode, mapping host port 80 to container port 5000,
# then open the browser at http://localhost
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
	poetry run python scripts/database_setup.py

# Run the journey metrics calculation script in debug mode
run:
	poetry run python scripts/journeys_measure.py --debug

# Run the journey setup script (process all journeys and measure)
journeys-measure:
	poetry run python -m scripts.journeys_measure --debug

# Run the journey setup script (process journeys file, update database)
journeys-setup:
	scripts/poetry_install.sh
	poetry run python -m scripts.journeys_setup --debug

# Clean up the environment
clean:
	rm -rf $(shell poetry env info --path)

# Initialize the database without dropping it
database-setup:
	poetry run python scripts/database_setup.py

# Apply Alembic migrations
database-migrate:
	poetry run alembic upgrade head

# Drop and recreate the database, then apply migrations
database-reset:
	psql -U $(DB_USER) -h $(DB_HOST) -p $(DB_PORT) -d postgres -c "DROP DATABASE IF EXISTS $(DB_NAME);"
	poetry run python scripts/database_setup.py

# Chain linters
lint:
	poetry run flake8 .
	poetry run black .
	poetry run isort .
	poetry run mypy .

# Push environment variables from .env.production to Heroku
heroku-config:
	@set -a && \
	. .env.production && \
	for var in $$(cat .env.production | grep -v '^#' | sed 's/=.*//'); do \
		heroku config:set $$var=$${!var}; \
	done