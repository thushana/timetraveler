#!/usr/bin/env python3
import argparse
import logging
import os
import sys
import time
from datetime import datetime

from core.journey.scheduler import JourneyScheduler
from core.config import settings

# Determine if running on Heroku (using the IS_HEROKU flag from settings)
is_heroku = settings.IS_HEROKU

# Set up logging handlers based on the environment
log_handlers = []
if is_heroku:
    # Heroku logs should go to stdout only.
    log_handlers.append(logging.StreamHandler(sys.stdout))
else:
    # Locally, log both to stdout and to a file for persistence.
    log_dir = os.path.join("/tmp", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "journey_measurements.log")
    log_handlers.append(logging.StreamHandler(sys.stdout))
    log_handlers.append(logging.FileHandler(log_file))

# Use logging settings from the config (LOG_LEVEL is a string, so convert it to a logging level)
log_level = getattr(logging, settings.LOG_LEVEL, logging.INFO)
logging.basicConfig(
    level=log_level,
    format=settings.LOG_FORMAT,
    datefmt=settings.LOG_DATE_FORMAT,
    handlers=log_handlers,
)
logger = logging.getLogger(__name__)


def format_time(seconds: float) -> str:
    """Format seconds into a detailed time string."""
    hours, remainder = divmod(seconds, 3600)
    minutes, remainder = divmod(remainder, 60)
    secs, milliseconds = divmod(remainder, 1)
    milliseconds = int(milliseconds * 1000)

    parts = []
    if hours > 0:
        parts.append(f"{int(hours)}h")
    if minutes > 0:
        parts.append(f"{int(minutes)}m")
    if secs > 0 or milliseconds > 0:
        parts.append(f"{int(secs)}s")
    if milliseconds > 0:
        parts.append(f"{milliseconds}ms")

    return " ".join(parts) if parts else "0ms"


def run_scheduler(max_retries: int = 3, retry_delay: int = 5) -> None:
    """
    Run the journey scheduler with retry logic.

    Args:
        max_retries: Maximum number of retry attempts.
        retry_delay: Delay in seconds between retries.
    """
    # Load configuration from settings
    debug_mode = settings.DEBUG
    max_workers = settings.MAX_WORKERS

    attempt = 0
    while attempt < max_retries:
        start_time = time.perf_counter()
        start_datetime = datetime.now()
        try:
            logger.info(
                f"Starting journey metrics calculation job at {start_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}"
            )

            # Initialize the scheduler with configuration from settings/env
            scheduler = JourneyScheduler(debug=debug_mode, max_workers=max_workers)
            scheduler.process_all_journeys()

            end_time = time.perf_counter()
            run_time = end_time - start_time
            end_datetime = datetime.now()

            logger.info("Successfully completed journey metrics calculation job")
            logger.info(f"Total run time: {format_time(run_time)}")
            logger.info(f"Start time: {start_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
            logger.info(f"End time: {end_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")

            # Optional: Warn if runtime exceeds a target (here, 1 second)
            if run_time > 1:
                logger.warning(f"Job completed but exceeded target runtime: {format_time(run_time)}")

            break

        except Exception as e:
            attempt += 1
            end_time = time.perf_counter()
            run_time = end_time - start_time
            logger.error(
                f"Error during journey metrics calculation job (attempt {attempt}/{max_retries}): {str(e)}"
            )
            logger.error(f"Failed after running for: {format_time(run_time)}")

            if attempt < max_retries:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Max retries reached. Exiting with error.")
                sys.exit(1)
        finally:
            # On Heroku, ensure we don’t approach the timeout limit
            if is_heroku and (time.perf_counter() - start_time) > settings.HEROKU_TIMEOUT_MARGIN:
                logger.error("Job approaching Heroku timeout limit")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run journey metrics calculation job")
    parser.add_argument("--max-retries", type=int, default=3, help="Maximum retry attempts")
    parser.add_argument("--retry-delay", type=int, default=5, help="Delay between retries in seconds")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    # Allow command-line override for debug mode
    if args.debug:
        settings.DEBUG = True

    run_scheduler(max_retries=args.max_retries, retry_delay=args.retry_delay)


if __name__ == "__main__":
    main()
