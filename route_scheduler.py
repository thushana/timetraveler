# Standard Library
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Third-party
import googlemaps

# Application
import keys
from route_metrics_calculator import RouteMetricsCalculator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RouteScheduler:
    def __init__(self, input_file: str = 'routes_enriched.json', 
                 output_dir: str = 'route_metrics',
                 max_workers: int = 40,
                 debug: bool = False):
        """Initialize the route scheduler."""
        self.input_file = input_file
        self.output_dir = Path(output_dir)
        self.max_workers = max_workers
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize Google Maps client
        api_key = keys.get_google_maps_api_key()
        if not api_key:
            raise ValueError("GOOGLE_MAPS_API_KEY environment variable is not set")
        self.gmaps = googlemaps.Client(key=api_key)
        
        # Initialize calculator
        self.calculator = RouteMetricsCalculator(self.gmaps, debug=debug)

    def load_routes(self) -> List[Dict[str, Any]]:
        """Load routes from the input file."""
        try:
            with open(self.input_file, 'r') as f:
                routes_data = json.load(f)
            return routes_data.get('routes', [])
        except FileNotFoundError:
            logger.error(f"Input file not found: {self.input_file}")
            raise
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON format in file: {self.input_file}")
            raise
        except Exception as e:
            logger.error(f"Error reading input file: {str(e)}")
            raise

    def save_route_metrics(self, route_metrics: Dict[str, Any]) -> None:
        """Save route metrics to a JSON file."""
        try:
            route_name = route_metrics['route_name'].replace(' ', '_').lower()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{route_name}_{timestamp}.json"
            
            output_path = self.output_dir / filename
            with open(output_path, 'w') as f:
                json.dump(route_metrics, f, indent=2)
            
            logger.info(f"Saved metrics for route '{route_metrics['route_name']}' to {output_path}")
        
        except Exception as e:
            logger.error(f"Error saving metrics for route '{route_metrics.get('route_name', 'unknown')}': {str(e)}")

    def process_single_route(self, route: Dict[str, Any]) -> None:
        """Process a single route and save its metrics."""
        try:
            route_name = route.get('route_name', 'Unnamed Route')
            logger.info(f"Processing route: {route_name}")
            
            metrics = self.calculator.process_route(route)
            self.save_route_metrics(metrics)
            
            logger.info(f"Completed processing route: {route_name}")
        
        except Exception as e:
            logger.error(f"Error processing route '{route.get('route_name', 'unknown')}': {str(e)}")

    def process_all_routes(self) -> None:
        """Process all routes in parallel using ThreadPoolExecutor."""
        try:
            routes = self.load_routes()
            logger.info(f"Starting to process {len(routes)} routes")
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [
                    executor.submit(self.process_single_route, route)
                    for route in routes
                ]
                
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logger.error(f"Error in thread: {str(e)}")
            
            logger.info("Completed processing all routes")
        
        except Exception as e:
            logger.error(f"Error in process_all_routes: {str(e)}")
            raise