#!/usr/bin/env python3

import logging
import sys
import time
from datetime import datetime
from route_scheduler import RouteScheduler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('route_metrics.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def format_time(seconds):
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

def main():
    """Main function to be called by cron."""
    start_time = time.perf_counter()
    start_datetime = datetime.now()
    
    try:
        logger.info(f"Starting route metrics calculation job at {start_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
        
        # Get debug mode from command line argument
        debug_mode = '--debug' in sys.argv
        scheduler = RouteScheduler(debug=debug_mode)
        scheduler.process_all_routes()
        
        end_time = time.perf_counter()
        run_time = end_time - start_time
        end_datetime = datetime.now()
        
        logger.info("Completed route metrics calculation job")
        logger.info(f"Total run time: {format_time(run_time)}")
        logger.info(f"Start time: {start_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
        logger.info(f"End time: {end_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
    
    except Exception as e:
        end_time = time.perf_counter()
        run_time = end_time - start_time
        logger.error(f"Critical error in route metrics calculation job: {str(e)}")
        logger.error(f"Failed after running for: {format_time(run_time)}")
        sys.exit(1)

if __name__ == "__main__":
    main()