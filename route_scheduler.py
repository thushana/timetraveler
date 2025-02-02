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
        
        self.calculator = RouteMetricsCalculator(self.gmaps, debug=debug)

    @staticmethod
    def format_duration(seconds: int) -> str:
        """Format duration in seconds to hours, minutes, seconds string."""
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"

    @staticmethod
    def meters_to_miles(meters: float) -> float:
        """Convert meters to miles."""
        return meters / 1609.34

    @staticmethod
    def kph_to_mph(kph: float) -> float:
        """Convert kilometers per hour to miles per hour."""
        return kph * 0.621371

    def print_route_summary(self, route_metrics: Dict[str, Any]) -> None:
        """Print a detailed summary of route metrics including imperial conversions."""
        print("\n" + "="* 80)
        print(f"Route: {route_metrics['route_name']}")
        print(f"Description: {route_metrics['route_description']}")
        print("=" * 80)

        if self.debug:
            print("\nDebug: Available keys in route_metrics:", route_metrics.keys())

        # Section 1: Point-to-point routes for all modes
        print("\nPOINT-TO-POINT ROUTES:")
        print("-" * 40)

        if self.debug:
            print("\nDebug: Available modes:", route_metrics['modes'].keys())
        
        # Print each mode's point-to-point metrics
        for mode, data in route_metrics['modes'].items():
            if data and 'metrics' in data:
                metrics = data['metrics']
                mode_display = mode.upper()
                print(f"\n{mode_display}:")
                print(f"Duration: {self.format_duration(metrics['duration_seconds'])}")
                print(f"Distance: {metrics['distance_meters']/1000:.1f} km ({self.meters_to_miles(metrics['distance_meters']):.1f} miles)")
                if 'speed_kph' in metrics:
                    print(f"Average Speed: {metrics['speed_kph']:.1f} kph ({self.kph_to_mph(metrics['speed_kph']):.1f} mph)")

        # Section 2: Routed driving with waypoints
        if route_metrics.get('driving_routed'):
            print("\n" + "=" * 80)
            print("DRIVING (ROUTED WITH WAYPOINTS):")
            print("-" * 40)
            
            routed = route_metrics['driving_routed']
            print("\nOverall Route Metrics:")
            print(f"Duration: {self.format_duration(routed['duration_seconds'])}")
            print(f"Distance: {routed['distance_meters']/1000:.1f} km ({self.meters_to_miles(routed['distance_meters']):.1f} miles)")
            print(f"Average Speed: {routed['speed_kph']:.1f} kph ({self.kph_to_mph(routed['speed_kph']):.1f} mph)")

            # Print detailed leg information for the routed path
            if route_metrics.get('driving_routed_legs'):
                if self.debug:
                    print(f"\nDebug: Found {len(route_metrics['driving_routed_legs'])} legs")
                
                print("\nDetailed Leg Information:")
                for i, leg in enumerate(route_metrics['driving_routed_legs'], 1):
                    print(f"\nLeg {i}:")
                    print(f"From: {leg['start_address']}")
                    print(f"To: {leg['end_address']}")
                    print(f"Duration: {self.format_duration(leg['duration_seconds'])}")
                    print(f"Distance: {leg['distance_meters']/1000:.1f} km ({self.meters_to_miles(leg['distance_meters']):.1f} miles)")
                    if 'speed_kph' in leg:
                        print(f"Speed: {leg['speed_kph']:.1f} kph ({self.kph_to_mph(leg['speed_kph']):.1f} mph)")
            elif self.debug:
                print("\nDebug: No leg details found in route_metrics['driving_routed_legs']")

        print("\n" + "=" * 80)

    def load_routes(self) -> List[Dict[str, Any]]:
        """Load routes from the input file."""
        try:
            with open(self.input_file, 'r') as f:
                routes_data = json.load(f)
            return routes_data.get('routes', [])
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
            
            logger.info(f"Saved metrics for route '{route_metrics['route_name']}'")
            
        except Exception as e:
            logger.error(f"Error saving metrics for route '{route_metrics.get('route_name', 'unknown')}': {str(e)}")

    def process_single_route(self, route: Dict[str, Any]) -> None:
        """Process a single route and save its metrics."""
        try:
            metrics = self.calculator.process_route(route)
            self.save_route_metrics(metrics)
            self.completed_routes.append(metrics)
            
        except Exception as e:
            logger.error(f"Error processing route '{route.get('route_name', 'unknown')}': {str(e)}")

    def process_all_routes(self) -> None:
        """Process all routes in parallel and print summaries at the end."""
        try:
            routes = self.load_routes()
            logger.info(f"Starting to process {len(routes)} routes")
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_route = {
                    executor.submit(self.process_single_route, route): route
                    for route in routes
                }
                
                for future in as_completed(future_to_route):
                    route = future_to_route[future]
                    try:
                        future.result()
                    except Exception as e:
                        logger.error(f"Error in thread processing route '{route.get('route_name', 'unknown')}': {str(e)}")
            
            # Print detailed summaries for all completed routes
            if self.debug:
                print("\nComplete Route Summaries:")
                for route_metrics in self.completed_routes:
                    self.print_route_summary(route_metrics)
            
            logger.info("Completed processing all routes")
            
        except Exception as e:
            logger.error(f"Error in process_all_routes: {str(e)}")
            raise