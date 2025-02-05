#!/usr/bin/env python3
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import googlemaps
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.journey.processor import JourneyProcessor
from database.models.base import Base

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def format_time(seconds: float) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, remainder = divmod(remainder, 60)
    seconds, milliseconds = divmod(remainder, 1)
    milliseconds = int(milliseconds * 1000)

    parts = []
    if hours > 0:
        parts.append(f"{int(hours)}h")
    if minutes > 0:
        parts.append(f"{int(minutes)}m")
    if seconds > 0 or milliseconds > 0:
        parts.append(f"{int(seconds)}s")
    if milliseconds > 0:
        parts.append(f"{milliseconds}ms")

    return " ".join(parts) if parts else "0ms"


def main() -> None:
    start_time = time.perf_counter()
    start_datetime = datetime.now()

    try:
        logger.info(f"Starting journey processing test at {start_datetime}")
        load_dotenv()

        DATABASE_URL = (
            f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
            f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        )

        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)

        gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))
        input_file = Path("data/raw/journeys.json")

        with SessionLocal() as db:
            processor = JourneyProcessor(db=db, gmaps_client=gmaps, debug=True)
            processed_journeys = processor.process_routes_file(input_file)

            for journey in processed_journeys:
                processor.print_journey_summary(journey)

        end_time = time.perf_counter()
        run_time = end_time - start_time

        logger.info("Successfully completed processing")
        logger.info(f"Total run time: {format_time(run_time)}")

    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
