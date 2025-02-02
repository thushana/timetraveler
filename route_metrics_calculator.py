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

    def calculate_mode_metrics(self, origin: str, destination: str, 
                             waypoint_ids: List[str], mode: str, 
                             departure_time: datetime, route_name: str) -> Tuple[str, Dict[str, Any]]:
        """Calculate metrics for a specific travel mode."""
        try:
            if self.debug:
                print(f"Calculating {route_name} - {mode} {'(routed with waypoints)' if mode == 'driving' else '(point-to-point)'}...")

            directions_kwargs = {
                'origin': origin,
                'destination': destination,
                'mode': mode,
                'departure_time': departure_time,
                'units': 'metric'
            }
            
            # Only add waypoints for routed driving
            if mode == 'driving' and waypoint_ids:
                directions_kwargs['waypoints'] = waypoint_ids

            result = self.gmaps.directions(**directions_kwargs)
            
            if result:
                route = result[0]
                metrics = self.calculate_route_metrics(route)
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
                
                if self.debug:
                    print(f"Found {len(leg_details)} legs for {mode} route")
                
                return mode, {
                    'metrics': metrics,
                    'leg_details': leg_details
                }
            
            if self.debug:
                print(f"No {mode} route found")
            return mode, None

        except Exception as e:
            if self.debug:
                print(f"Error calculating {mode} route: {str(e)}")
            return mode, {'error': str(e)}

    def process_route(self, route_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single route and calculate its metrics."""
        try:
            route_name = route_data.get('route_name', 'Unnamed Route')
            if self.debug:
                print(f"\nProcessing route: {route_name}")

            route_metrics = {
                'route_name': route_data.get('route_name', 'Unnamed Route'),
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

            # Calculate standard point-to-point routes for each mode
            modes = ['driving', 'bicycling', 'walking', 'transit']
            driving_routed_result = None  # Store the routed result separately
            
            with ThreadPoolExecutor(max_workers=self.max_mode_workers) as executor:
                future_to_mode = {
                    executor.submit(
                        self.calculate_mode_metrics,
                        origin,
                        destination,
                        [] if mode != 'driving' else waypoint_ids,  # Only pass waypoints for driving
                        mode,
                        departure_time,
                        route_name
                    ): mode for mode in modes
                }
                
                for future in as_completed(future_to_mode):
                    mode = future_to_mode[future]
                    mode_result = future.result()
                    
                    if mode == 'driving':
                        # Store the routed driving result separately
                        driving_routed_result = mode_result[1]
                        
                        # Calculate point-to-point driving separately
                        point_result = self.gmaps.directions(
                            origin,
                            destination,
                            mode="driving",
                            departure_time=departure_time,
                            units='metric'
                        )
                        
                        if point_result:
                            route_metrics['modes'][mode] = {
                                'metrics': self.calculate_route_metrics(point_result[0])
                            }
                    else:
                        route_metrics['modes'][mode] = mode_result[1]

            # Add routed driving metrics separately
            if driving_routed_result and 'metrics' in driving_routed_result:
                route_metrics['driving_routed'] = driving_routed_result['metrics']
                route_metrics['driving_routed_legs'] = driving_routed_result['leg_details']
                
                if self.debug:
                    print(f"Stored {len(driving_routed_result['leg_details'])} legs for routed driving")

            return route_metrics

        except Exception as e:
            if self.debug:
                print(f"Error processing route: {str(e)}")
            return {
                'route_name': route_data.get('route_name', 'Unnamed Route'),
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }