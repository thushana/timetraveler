.PHONY: setup run clean setup-db migrate reset-db

# Set up virtual environment, install dependencies, and initialize database
setup:
	python3 -m venv env && . env/bin/activate && pip install -r requirements.txt
	python scripts/setup_db.py

# Run the journey cron script in debug mode
run:
	bash -c '. env/bin/activate && python -m scripts.journey_cron --debug'

# Clean up the environment
clean:
	rm -rf env

# Initialize the database without dropping it
setup-db:
	python scripts/setup_db.py

# Apply Alembic migrations
migrate:
	alembic upgrade head

# Drop and recreate the database, then apply migrations
reset-db:
	psql -U $(DB_USER) -h $(DB_HOST) -d postgres -c "DROP DATABASE IF EXISTS timetraveler;"
	python scripts/setup_db.py

# Chain linters
lint:
	flake8 .
	black .
	isort .
	mypy .