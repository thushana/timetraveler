# ---------------------------------------
# PHONY TARGETS
# ---------------------------------------

.PHONY: setup clean lint journeys-setup journeys-measure
.PHONY: database-setup database-migrate database-reset database-state database-recent
.PHONY: docker-build docker-run docker-stop docker-rebuild docker-logs
.PHONY: heroku-config

# ---------------------------------------
# CONFIGURATION
# ---------------------------------------

# Define DB_* variables by extracting them from your Python settings.
# These variables are dynamically fetched using Poetry to keep them in sync with your application configuration.
DB_USER := $(shell poetry run python -c "from core.config import settings; print(settings.DB_USER)")
DB_HOST := $(shell poetry run python -c "from core.config import settings; print(settings.DB_HOST)")
DB_PORT := $(shell poetry run python -c "from core.config import settings; print(settings.DB_PORT)")
DB_NAME := $(shell poetry run python -c "from core.config import settings; print(settings.DB_NAME)")

# ---------------------------------------
# DOCKER
# ---------------------------------------

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

# ---------------------------------------
# DATABASE
# ---------------------------------------

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

# Fetch and copy database schema
# Usage: make database-state <table_name>
database-state:
	@if ! command -v psql &> /dev/null; then \
		echo "Error: 'psql' is not installed."; \
		exit 1; \
	fi; \
	TABLE_NAME=$$(echo "$@" | awk '{print $$1}'); \
	QUERY="SELECT table_name, column_name, data_type \
	       FROM information_schema.columns \
	       WHERE table_schema = 'public'"; \
	if [ -n "$$TABLE_NAME" ]; then \
		QUERY="$$QUERY AND table_name = '$$TABLE_NAME'"; \
	fi; \
	QUERY="$$QUERY ORDER BY table_name, ordinal_position;"; \
	SCHEMA_OUTPUT=$$(psql -d $(DB_NAME) -P pager=off -c "$$QUERY"); \
	echo "$$SCHEMA_OUTPUT"; \
	echo "$$SCHEMA_OUTPUT" | pbcopy; \
	echo "Schema for '$${TABLE_NAME:-all tables}' copied to clipboard."; \
	osascript -e 'tell application "Google Chrome" to activate' 2>/dev/null || echo "Google Chrome is not running."

# Fetch most recent rows from a table
# Usage: make database-recent <table_name> <row_limit>
database-recent:
	@if ! command -v psql &> /dev/null; then \
		echo "Error: 'psql' is not installed."; \
		exit 1; \
	fi; \
	TABLE_NAME=$$(echo "$@" | awk '{print $$1}'); \
	ROW_LIMIT=$$(echo "$@" | awk '{print $$2}'); \
	ROW_LIMIT=$${ROW_LIMIT:-1}; \
	if [ -z "$$TABLE_NAME" ]; then \
		echo "Usage: make database-recent <table_name> [row_limit]"; \
		exit 1; \
	fi; \
	QUERY="SELECT json_agg(t) FROM (SELECT * FROM $$TABLE_NAME ORDER BY id DESC LIMIT $$ROW_LIMIT) t;"; \
	RECENT_OUTPUT=$$(psql -d $(DB_NAME) -t -A -c "$$QUERY"); \
	if command -v jq &> /dev/null; then \
		FORMATTED_OUTPUT=$$(echo "$$RECENT_OUTPUT" | jq); \
	else \
		FORMATTED_OUTPUT="$$RECENT_OUTPUT"; \
	fi; \
	echo "$$FORMATTED_OUTPUT"; \
	echo "$$FORMATTED_OUTPUT" | pbcopy; \
	echo "Most recent $$ROW_LIMIT row(s) from '$$TABLE_NAME' copied to clipboard."; \
	osascript -e 'tell application "Google Chrome" to activate' 2>/dev/null || echo "Google Chrome is not running."

# ---------------------------------------
# DEVELOPMENT
# ---------------------------------------

# Set up the environment and install dependencies using Poetry
setup:
	poetry install
	poetry run python scripts/database_setup.py

# Clean up the environment
clean:
	rm -rf $(shell poetry env info --path)

# Chain linters
lint:
	poetry run flake8 .
	poetry run black .
	poetry run isort .
	poetry run mypy .

# ---------------------------------------
# JOURNEYS
# ---------------------------------------

# Process journeys file and update database
journeys-setup:
	export PATH="/app/.local/bin:$(PATH)" && \
	scripts/poetry_install.sh && \
	poetry install --only main && \
	poetry run python -m scripts.journeys_setup --debug

# Process all journeys and measure metrics
journeys-measure:
	poetry run python -m scripts.journeys_measure --debug

# ---------------------------------------
# HEROKU
# ---------------------------------------

# Push environment variables from .env.production to Heroku
heroku-config:
	@set -a && \
	. .env.production && \
	for var in $$(cat .env.production | grep -v '^#' | sed 's/=.*//'); do \
		heroku config:set $$var=$${!var}; \
	done
