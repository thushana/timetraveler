# Standard Library
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Third-party
import googlemaps

# Application
from core.config import settings
from core.journey.calculator import JourneyMetricsCalculator
from core.journey.processor import JourneyProcessor
from core.journey.reporter import JourneyReporter

logger = logging.getLogger(__name__)

class JourneyScheduler:
    def __init__(
        self,
        input_file: Path = None,
        output_dir: Path = None,
        max_workers: int = None,
        debug: bool = None
    ):
        """Initialize scheduler with optional configuration overrides.
        
        Args:
            input_file: Optional path to input file (default from settings)
            output_dir: Optional path to output directory (default from settings)
            max_workers: Optional thread pool size (default from settings)
            debug: Optional debug mode (default from settings)
        """
        self.input_file = input_file or settings.PROCESSED_JOURNEYS_PATH
        self.output_dir = output_dir or settings.METRICS_DATA_DIR
        self.max_workers = max_workers if max_workers is not None else settings.MAX_WORKERS
        self.debug = debug if debug is not None else settings.DEBUG
        self.completed_routes = []

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if self.debug:
            logger.info("Initializing JourneyScheduler:")
            logger.info(f"Input file: {self.input_file}")
            logger.info(f"Output directory: {self.output_dir}")
            logger.info(f"Max workers: {self.max_workers}")
            logger.info(f"Debug mode: {self.debug}")
        
        # Initialize Google Maps client
        api_key = settings.get_google_maps_api_key()
        self.gmaps = googlemaps.Client(key=api_key)
        
        # Initialize components
        self.calculator = JourneyMetricsCalculator(
            self.gmaps,
            max_workers=self.max_workers,
            debug=self.debug
        )
        self.reporter = JourneyReporter(debug=self.debug)
        self.processor = JourneyProcessor(self.gmaps, debug=self.debug)

    def load_routes(self) -> List[Dict[str, Any]]:
        """Load journeys from input file with error handling."""
        try:
            if not self.input_file.exists():
                raise FileNotFoundError(f"Input file not found: {self.input_file}")
                
            with self.input_file.open('r') as f:
                journeys_data = json.load(f)
            
            journeys = journeys_data.get('journeys', [])
            if not journeys:
                logger.warning("No journeys found in input file")
                
            if self.debug:
                logger.info(f"Loaded {len(journeys)} journeys from {self.input_file}")
                
            return journeys
            
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in input file: {self.input_file}")
            raise
        except Exception as e:
            logger.error(f"Error reading input file: {str(e)}")
            raise

    def save_route_metrics(self, journey_metrics: Dict[str, Any]) -> None:
        """Save journey metrics to JSON file with error handling."""
        try:
            # Get metrics path using settings helper
            output_path = settings.get_metrics_path(journey_metrics['journey_name'])
            
            if self.debug:
                logger.info(f"Saving metrics to: {output_path}")

            # Use atomic write operation
            temp_path = output_path.with_suffix('.tmp')
            with temp_path.open('w') as f:
                json.dump(journey_metrics, f, indent=2)
            temp_path.rename(output_path)
            
            logger.info(f"Saved metrics for journey '{journey_metrics['journey_name']}'")
            
        except Exception as e:
            logger.error(f"Error saving metrics for journey '{journey_metrics.get('journey_name', 'unknown')}': {str(e)}")
            raise

    def process_single_route(self, journey: Dict[str, Any]) -> None:
        """Process a single journey using the calculator."""
        journey_name = journey.get('journey_name', 'unknown')
        try:
            logger.info(f"Starting to process journey: {journey_name}")
            
            metrics = self.calculator.process_route(journey)
            self.save_route_metrics(metrics)
            self.completed_routes.append(metrics)
            
            logger.info(f"Completed processing journey: {journey_name}")
            
        except Exception as e:
            logger.error(f"Error processing journey '{journey_name}': {str(e)}")
            error_metrics = {
                'journey_name': journey_name,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.completed_routes.append(error_metrics)
            raise

    def process_all_routes(self) -> None:
        """Process all journeys and generate metrics."""
        start_time = datetime.now()
        
        try:
            journeys = self.load_routes()
            total_routes = len(journeys)
            logger.info(f"Starting to process {total_routes} journeys")
            
            # Process journeys using the calculator's thread pool
            with self.calculator as calc:
                for journey in journeys:
                    self.process_single_route(journey)
            
            # Generate summary report
            self.reporter.print_batch_summary(self.completed_routes)
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds() * 1000
            logger.info(f"Completed processing {total_routes} journeys in {processing_time:.2f}ms")
            
            if total_routes > 0:
                logger.info(f"Average time per journey: {processing_time/total_routes:.2f}ms")
            
        except Exception as e:
            logger.error(f"Error in process_all_routes: {str(e)}")
            raise