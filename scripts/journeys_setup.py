#!/usr/bin/env python3
"""
A one-off script to process journeys from a JSON file and set up the database
with journeys ready for measurement. This script leverages the JourneyProcessor
from core/journey/processor.py and is intended to be run as a one-off or in a Heroku setup.
"""

import argparse
import logging
import os
import sys
from pathlib import Path

import googlemaps

from core.config import settings
from core.journey.processor import JourneyProcessor

# Configure logging similar to journeys_measure.py
log_handlers = []
if settings.IS_HEROKU:
    # On Heroku, log to stdout only.
    log_handlers.append(logging.StreamHandler(sys.stdout))
else:
    # Locally, log both to stdout and to a file.
    log_dir = os.path.join("/tmp", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "journeys_setup.log")
    log_handlers.append(logging.StreamHandler(sys.stdout))
    log_handlers.append(logging.FileHandler(log_file))

log_level = getattr(logging, settings.LOG_LEVEL, logging.INFO)
logging.basicConfig(
    level=log_level,
    format=settings.LOG_FORMAT,
    datefmt=settings.LOG_DATE_FORMAT,
    handlers=log_handlers,
)
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Set up the database with journeys to measure using JourneyProcessor"
    )
    parser.add_argument(
        "--journeys-file",
        type=str,
        default="data/raw/journeys.json",
        help="Path to the journeys JSON file (default: data/raw/journeys.json)",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug mode (overrides settings.DEBUG)"
    )
    args = parser.parse_args()

    # Allow command-line override for debug mode.
    if args.debug:
        settings.DEBUG = True

    logger.info("Starting journeys setup script")

    # Import the session (assuming your database/session.py defines SessionLocal)
    try:
        from database.session import SessionLocal
    except ImportError:
        logger.error("Could not import SessionLocal from database/session.py")
        sys.exit(1)

    # Create a database session.
    session = SessionLocal()

    # Create a Google Maps client using an API key from settings.
    try:
        # Make sure your settings file defines GOOGLE_MAPS_API_KEY.
        gmaps_client = googlemaps.Client(key=settings.get_google_maps_api_key())
    except Exception as e:
        logger.error("Error creating Google Maps client: %s", e)
        sys.exit(1)

    # Instantiate the JourneyProcessor.
    processor = JourneyProcessor(db=session, gmaps_client=gmaps_client, debug=settings.DEBUG)

    # Build the path to the journeys file.
    journeys_file_path = Path(args.journeys_file)
    if not journeys_file_path.exists():
        logger.error("Journeys file does not exist: %s", journeys_file_path)
        sys.exit(1)

    # Process the journeys file.
    try:
        journeys = processor.process_routes_file(journeys_filename=journeys_file_path)
        for journey in journeys:
            processor.print_journey_summary(journey)
    except Exception as e:
        logger.error("Error processing journeys file: %s", e)
        sys.exit(1)
    finally:
        session.close()

    logger.info("Journeys setup completed successfully")


if __name__ == "__main__":
    main()
