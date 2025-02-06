#!/usr/bin/env python3
import logging
import sys
import time
import os
from datetime import datetime
from typing import Optional

from core.journey.scheduler import JourneyScheduler
from core.config import settings

# Define log directory and ensure it exists
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# Log file path
LOG_FILE = os.path.join(LOG_DIR, 'journey_measurements.log')

# Configure logging with timestamp and log level
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE)
    ]
)

logger = logging.getLogger(__name__)

def run_scheduler(max_retries: int = 3, retry_delay: int = 5) -> None:
    """
    Run the journey scheduler with retry logic
    
    Args:
        max_retries: Maximum number of retry attempts
        retry_delay: Delay in seconds between retries
    """
    attempt = 0
    while attempt < max_retries:
        try:
            logger.info(f"Starting measurement run at {datetime.now()}")
            
            # Initialize scheduler with production settings
            debug_mode = settings.DEBUG if hasattr(settings, 'DEBUG') else False
            scheduler = JourneyScheduler(debug=debug_mode)
            
            # Process journeys
            scheduler.process_all_journeys()
            
            logger.info("Measurement run completed successfully")
            break
            
        except Exception as e:
            attempt += 1
            logger.error(f"Error during measurement run (attempt {attempt}/{max_retries}): {str(e)}")
            
            if attempt < max_retries:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Max retries reached. Exiting with error.")
                sys.exit(1)

def main() -> None:
    try:
        run_scheduler()
    except Exception as e:
        logger.error(f"Fatal error in main: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()