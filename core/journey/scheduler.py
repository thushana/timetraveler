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
from core.journey.calculator import RouteMetricsCalculator
from core.journey.processor import RouteProcessor
from core.journey.reporter import RouteReporter

logger = logging.getLogger(__name__)

class RouteScheduler:
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
            logger.info("Initializing RouteScheduler:")
            logger.info(f"Input file: {self.input_file}")
            logger.info(f"Output directory: {self.output_dir}")
            logger.info(f"Max workers: {self.max_workers}")
            logger.info(f"Debug mode: {self.debug}")
        
        # Initialize Google Maps client
        api_key = settings.get_google_maps_api_key()
        self.gmaps = googlemaps.Client(key=api_key)
        
        # Initialize components
        self.calculator = RouteMetricsCalculator(
            self.gmaps,
            max_workers=self.max_workers,
            debug=self.debug
        )
        self.reporter = RouteReporter(debug=self.debug)
        self.processor = RouteProcessor(self.gmaps, debug=self.debug)

    def load_routes(self) -> List[Dict[str, Any]]:
        """Load routes from input file with error handling."""
        try:
            if not self.input_file.exists():
                raise FileNotFoundError(f"Input file not found: {self.input_file}")
                
            with self.input_file.open('r') as f:
                routes_data = json.load(f)
            
            routes = routes_data.get('routes', [])
            if not routes:
                logger.warning("No routes found in input file")
                
            if self.debug:
                logger.info(f"Loaded {len(routes)} routes from {self.input_file}")
                
            return routes
            
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in input file: {self.input_file}")
            raise
        except Exception as e:
            logger.error(f"Error reading input file: {str(e)}")
            raise

    def save_route_metrics(self, route_metrics: Dict[str, Any]) -> None:
        """Save route metrics to JSON file with error handling."""
        try:
            # Get metrics path using settings helper
            output_path = settings.get_metrics_path(route_metrics['route_name'])
            
            if self.debug:
                logger.info(f"Saving metrics to: {output_path}")

            # Use atomic write operation
            temp_path = output_path.with_suffix('.tmp')
            with temp_path.open('w') as f:
                json.dump(route_metrics, f, indent=2)
            temp_path.rename(output_path)
            
            logger.info(f"Saved metrics for route '{route_metrics['route_name']}'")
            
        except Exception as e:
            logger.error(f"Error saving metrics for route '{route_metrics.get('route_name', 'unknown')}': {str(e)}")
            raise

    def process_single_route(self, route: Dict[str, Any]) -> None:
        """Process a single route using the calculator."""
        route_name = route.get('route_name', 'unknown')
        try:
            logger.info(f"Starting to process route: {route_name}")
            
            metrics = self.calculator.process_route(route)
            self.save_route_metrics(metrics)
            self.completed_routes.append(metrics)
            
            logger.info(f"Completed processing route: {route_name}")
            
        except Exception as e:
            logger.error(f"Error processing route '{route_name}': {str(e)}")
            error_metrics = {
                'route_name': route_name,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.completed_routes.append(error_metrics)
            raise

    def process_all_routes(self) -> None:
        """Process all routes and generate metrics."""
        start_time = datetime.now()
        
        try:
            routes = self.load_routes()
            total_routes = len(routes)
            logger.info(f"Starting to process {total_routes} routes")
            
            # Process routes using the calculator's thread pool
            with self.calculator as calc:
                for route in routes:
                    self.process_single_route(route)
            
            # Generate summary report
            self.reporter.print_batch_summary(self.completed_routes)
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds() * 1000
            logger.info(f"Completed processing {total_routes} routes in {processing_time:.2f}ms")
            
            if total_routes > 0:
                logger.info(f"Average time per route: {processing_time/total_routes:.2f}ms")
            
        except Exception as e:
            logger.error(f"Error in process_all_routes: {str(e)}")
            raise