# Standard Library
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Third-party
import googlemaps

# Application
import keys
from route_metrics_calculator import RouteMetricsCalculator
from route_reporter import RouteReporter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RouteScheduler:
    def __init__(self, input_file: str = 'routes_enriched.json', 
    def __init__(
        self,
        input_file: str = 'routes_enriched.json',
        output_dir: str = 'route_metrics',
        max_workers: int = 4,
        debug: bool = False
    ):
        self.input_file = input_file
        self.output_dir = Path(output_dir)
        self.max_workers = max_workers
        self.debug = debug
        self.completed_routes = []
        self.output_dir.mkdir(exist_ok=True)
        
        api_key = keys.get_google_maps_api_key()
        if not api_key:
            raise ValueError("GOOGLE_MAPS_API_KEY environment variable is not set")
        
        self.gmaps = googlemaps.Client(key=api_key)
        self.calculator = RouteMetricsCalculator(
            self.gmaps,
            max_workers=self.max_workers,
            debug=debug
        )
        self.reporter = RouteReporter(debug=debug)

    def load_routes(self) -> List[Dict[str, Any]]:
        """Load routes from input file with error handling."""
        try:
            with open(self.input_file, 'r') as f:
                routes_data = json.load(f)
            
            routes = routes_data.get('routes', [])
            if not routes:
                logger.warning("No routes found in input file")
            return routes
            
        except FileNotFoundError:
            logger.error(f"Input file not found: {self.input_file}")
            raise
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in input file: {self.input_file}")
            raise
        except Exception as e:
            logger.error(f"Error reading input file: {str(e)}")
            raise

    def save_route_metrics(self, route_metrics: Dict[str, Any]) -> None:
        """Save route metrics to JSON file with error handling."""
        try:
            route_name = route_metrics['route_name'].replace(' ', '_').lower()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{route_name}_{timestamp}.json"
            
            output_path = self.output_dir / filename
            
            # Use atomic write operation
            temp_path = output_path.with_suffix('.tmp')
            with open(temp_path, 'w') as f:
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
        """Process all routes."""
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
            processing_time = (end_time - start_time).total_seconds() * 1000  # Convert to milliseconds
            logger.info(f"Completed processing {total_routes} routes in {processing_time:.2f}ms")
            logger.info(f"Average time per route: {processing_time/total_routes:.2f}ms")
            
        except Exception as e:
            logger.error(f"Error in process_all_routes: {str(e)}")
            raise