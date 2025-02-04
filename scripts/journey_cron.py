#!/usr/bin/env python3

import logging
import sys
import time
from datetime import datetime

from core.journey.scheduler import RouteScheduler

# Configure logging for Heroku environment
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def format_time(seconds: float) -> str:
    """Format seconds into a detailed time string."""
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
    """Main function to be called by Heroku Scheduler."""
    start_time = time.perf_counter()
    start_datetime = datetime.now()
    
    try:
        logger.info(f"Starting route metrics calculation job at {start_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
        
        # Get debug mode from command line argument
        debug_mode = '--debug' in sys.argv
        
        # Initialize scheduler with Heroku Eco dyno optimized settings
        scheduler = RouteScheduler(
            max_workers=4,  # Optimized for Heroku Eco dyno
            debug=debug_mode
        )
        
        # Process routes
        scheduler.process_all_routes()
        
        # Calculate and log metrics
        end_time = time.perf_counter()
        run_time = end_time - start_time
        end_datetime = datetime.now()
        
        logger.info("Successfully completed route metrics calculation job")
        logger.info(f"Total run time: {format_time(run_time)}")
        logger.info(f"Start time: {start_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
        logger.info(f"End time: {end_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
        
        # Exit with success if runtime is within target
        if run_time > 1:
            logger.warning(f"Job completed but exceeded target runtime: {format_time(run_time)}")
        
    except Exception as e:
        end_time = time.perf_counter()
        run_time = end_time - start_time
        
        logger.error(f"Critical error in route metrics calculation job: {str(e)}")
        logger.error(f"Failed after running for: {format_time(run_time)}")
        sys.exit(1)
        
    finally:
        # Ensure we're under Heroku's timeout limit
        if time.perf_counter() - start_time > 25:  # 25 second safety margin
            logger.error("Job approaching Heroku timeout limit")

if __name__ == "__main__":
    main()