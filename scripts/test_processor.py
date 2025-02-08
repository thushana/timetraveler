#!/usr/bin/env python3
import logging
import sys
import time
from datetime import datetime

from sqlalchemy.orm import Session
from dotenv import load_dotenv

from core.journey.scheduler import JourneyScheduler
from database.session import get_db  # Use existing DB session

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

def main() -> None:
    start_time = time.perf_counter()
    start_datetime = datetime.now()

    try:
        logger.info(f"Starting journey processing test at {start_datetime}")
        load_dotenv()

        # Use existing database session
        with get_db() as db:
            scheduler = JourneyScheduler(debug=True)
            scheduler.process_all_journeys()

        end_time = time.perf_counter()
        run_time = end_time - start_time

        logger.info("Successfully completed processing")
        logger.info(f"Total run time: {run_time:.2f}s")

    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
