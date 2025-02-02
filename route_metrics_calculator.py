# Standard Library
from datetime import datetime
from typing import Dict, Any, Tuple, List
from concurrent.futures import ThreadPoolExecutor, as_completed

# Third-party
import googlemaps

class RouteMetricsCalculator:
    def __init__(self, gmaps_client: googlemaps.Client, max_mode_workers: int = 40, debug: bool = False):
        self.gmaps = gmaps_client
        self.max_mode_workers = max_mode_workers
        self.debug = debug

    @staticmethod
    def calculate_speed(distance_meters: float, duration_seconds: float) -> float:
        """Calculate speed in kilometers per hour."""
        return (distance_meters / 1000) / (duration_seconds / 3600)

    @staticmethod
    def calculate_route_metrics(route: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate metrics for a route."""
        total_duration = sum(leg.get('duration', {}).get('value', 0) for leg in route.get('legs', []))
        total_distance = sum(leg.get('distance', {}).get('value', 0) for leg in route.get('legs', []))
        average_speed = RouteMetricsCalculator.calculate_speed(total_distance, total_duration)
        
        return {
            'duration_seconds': total_duration,
            'distance_meters': total_distance,
            'speed_kph': average_speed
        }

    def get_route_leg_details(self, route: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract leg details from a route."""
        leg_details = []
        for leg in route.get('legs', []):
            leg_distance = leg.get('distance', {}).get('value', 0)
            leg_duration = leg.get('duration', {}).get('value', 0)
            leg_metrics = {
                'start_address': leg.get('start_address'),
                'end_address': leg.get('end_address'),
                'duration_seconds': leg_duration,
                'distance_meters': leg_distance,
                'speed_kph': self.calculate_speed(leg_distance, leg_duration)
            }
            leg_details.append(leg_metrics)
        return leg_details

    def calculate_mode_metrics(self, origin: str, destination: str, 
                             waypoint_ids: List[str], mode: str, 
                             departure_time: datetime, is_routed: bool = False) -> Dict[str, Any]:
        """Calculate metrics for a specific travel mode."""
        try:
            if self.debug:
                print(f"Calculating {mode} {'(routed)' if is_routed else '(direct)'} route...")

            directions_kwargs = {
                'origin': origin,
                'destination': destination,
                'mode': mode,
                'departure_time': departure_time,
                'units': 'metric'
            }
            
            # Only add waypoints for routed paths
            if is_routed and waypoint_ids:
                directions_kwargs['waypoints'] = waypoint_ids

            result = self.gmaps.directions(**directions_kwargs)
            
            if result:
                route = result[0]
                return {
                    'metrics': self.calculate_route_metrics(route),
                    'leg_details': self.get_route_leg_details(route)
                }
            
            if self.debug:
                print(f"No route found for {mode} {'(routed)' if is_routed else '(direct)'}")
            return None

        except Exception as e:
            if self.debug:
                print(f"Error calculating {mode} route: {str(e)}")
            return {'error': str(e)}

    def process_route(self, route_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single route and calculate its metrics."""
        try:
            route_name = route_data.get('route_name', 'Unnamed Route')
            if self.debug:
                print(f"\nProcessing route: {route_name}")

            route_metrics = {
                'route_name': route_name,
                'route_description': route_data.get('route_description', 'No description available'),
                'timestamp': datetime.now().isoformat(),
                'modes': {},
                'status': 'success'
            }

            waypoints = route_data.get('waypoints', [])
            place_ids = [wp.get('place_id') for wp in waypoints if wp.get('place_id')]
            
            if not place_ids:
                route_metrics['status'] = 'error'
                route_metrics['error'] = 'No place IDs found in route'
                if self.debug:
                    print("No place IDs found in route")
                return route_metrics
            
            origin = f"place_id:{place_ids[0]}"
            destination = f"place_id:{place_ids[-1]}"
            waypoint_ids = [f"place_id:{pid}" for pid in place_ids[1:-1]]
            departure_time = datetime.now()

            # Calculate metrics for all modes
            modes = ['driving', 'bicycling', 'walking', 'transit']
            
            for mode in modes:
                # Calculate direct route
                direct_result = self.calculate_mode_metrics(
                    origin, destination, [], mode, departure_time, is_routed=False
                )
                
                if direct_result:
                    route_metrics['modes'][mode] = direct_result

                # Calculate routed version for driving
                if mode == 'driving' and waypoint_ids:
                    routed_result = self.calculate_mode_metrics(
                        origin, destination, waypoint_ids, mode, 
                        departure_time, is_routed=True
                    )
                    
                    if routed_result:
                        route_metrics['modes']['driving_routed'] = routed_result

            return route_metrics

        except Exception as e:
            if self.debug:
                print(f"Error processing route: {str(e)}")
            return {
                'route_name': route_name,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }