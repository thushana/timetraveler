# Standard Library
from datetime import datetime
from typing import Dict, Any, Tuple, List
from concurrent.futures import ThreadPoolExecutor, as_completed

# Third-party
import googlemaps

class RouteMetricsCalculator:
    def __init__(self, gmaps_client: googlemaps.Client, max_mode_workers: int = 40, debug: bool = False):
        """Initialize the calculator with a Google Maps client."""
        self.gmaps = gmaps_client
        self.max_mode_workers = max_mode_workers
        self.debug = debug

    @staticmethod
    def calculate_speed(distance: float, duration: float) -> Tuple[float, float]:
        """Calculate speed in kph and mph."""
        kph = (distance / 1000) / (duration / 3600)
        mph = (distance / 1609.34) / (duration / 3600)
        return kph, mph

    @staticmethod
    def calculate_route_metrics(route: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate metrics for a route."""
        total_duration = sum(leg.get('duration', {}).get('value', 0) for leg in route.get('legs', []))
        total_distance = sum(leg.get('distance', {}).get('value', 0) for leg in route.get('legs', []))
        average_kph, average_mph = RouteMetricsCalculator.calculate_speed(total_distance, total_duration)
        
        hours, remainder = divmod(total_duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return {
            'total_duration': total_duration,
            'total_distance': total_distance,
            'average_kph': average_kph,
            'average_mph': average_mph,
            'hours': int(hours),
            'minutes': int(minutes),
            'seconds': int(seconds)
        }

    def calculate_mode_metrics(self, origin: str, destination: str, 
                             waypoint_ids: List[str], mode: str, 
                             departure_time: datetime) -> Tuple[str, Dict[str, Any]]:
        """Calculate metrics for a specific travel mode."""
        try:
            if self.debug:
                print(f"\nCalculating {mode} route...")

            result = self.gmaps.directions(
                origin,
                destination,
                waypoints=waypoint_ids if mode == 'driving' else None,
                mode=mode,
                departure_time=departure_time
            )
            
            if result:
                metrics = self.calculate_route_metrics(result[0])
                leg_details = []
                
                for leg in result[0].get('legs', []):
                    leg_distance = leg.get('distance', {}).get('value', 0)
                    leg_duration = leg.get('duration', {}).get('value', 0)
                    leg_metrics = {
                        'start_address': leg.get('start_address'),
                        'end_address': leg.get('end_address'),
                        'duration': leg.get('duration', {}).get('text'),
                        'duration_seconds': leg_duration,
                        'distance': leg.get('distance', {}).get('text'),
                        'distance_miles': leg_distance / 1609.34
                    }
                    
                    if mode != 'transit':
                        leg_kph, leg_mph = self.calculate_speed(leg_distance, leg_duration)
                        leg_metrics.update({
                            'speed_kph': leg_kph,
                            'speed_mph': leg_mph
                        })
                    
                    leg_details.append(leg_metrics)
                    
                    if self.debug:
                        print(f"\nLeg from {leg_metrics['start_address']} to {leg_metrics['end_address']}:")
                        print(f"Time: {leg_metrics['duration']} ({leg_metrics['duration_seconds']} seconds)")
                        print(f"Distance: {leg_metrics['distance']} ({leg_metrics['distance_miles']:.3f} miles)")
                        if mode != 'transit':
                            print(f"Speed: {leg_metrics['speed_kph']:.2f} kph ({leg_metrics['speed_mph']:.2f} mph)")
                
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
            if self.debug:
                print(f"\nProcessing route: {route_data.get('route_name', 'Unnamed Route')}")
                print(f"Description: {route_data.get('route_description', 'No description available')}")

            route_metrics = {
                'route_name': route_data.get('route_name', 'Unnamed Route'),
                'route_description': route_data.get('route_description', 'No description available'),
                'timestamp': datetime.now().isoformat(),
                'modes': {},
                'point_to_point': None,
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

            if self.debug:
                print("\n=== Route Summary ===")

            # Calculate routes for different modes in parallel
            modes = ['driving', 'bicycling', 'walking', 'transit']
            with ThreadPoolExecutor(max_workers=self.max_mode_workers) as executor:
                future_to_mode = {
                    executor.submit(
                        self.calculate_mode_metrics,
                        origin,
                        destination,
                        waypoint_ids,
                        mode,
                        departure_time
                    ): mode for mode in modes
                }
                
                for future in as_completed(future_to_mode):
                    mode, result = future.result()
                    route_metrics['modes'][mode] = result
                    
                    if self.debug and result and 'metrics' in result:
                        metrics = result['metrics']
                        print(f"\nMode: {mode.capitalize()}")
                        print(f"Total time: {metrics['hours']}h {metrics['minutes']}m {metrics['seconds']}s")
                        print(f"Total time in seconds: {metrics['total_duration']} seconds")
                        print(f"Total distance: {metrics['total_distance'] / 1000:.1f} km ({metrics['total_distance'] / 1609.34:.3f} miles)")
                        print(f"Average speed: {metrics['average_kph']:.2f} kph ({metrics['average_mph']:.2f} mph)")

            if self.debug:
                print("\n=== Point-to-Point Summary ===")

            # Calculate point-to-point metrics
            point_result = self.gmaps.directions(
                origin,
                destination,
                mode="driving",
                departure_time=departure_time
            )
            
            if point_result:
                route_metrics['point_to_point'] = self.calculate_route_metrics(point_result[0])
                if self.debug:
                    metrics = route_metrics['point_to_point']
                    print(f"Point-to-point driving time: {metrics['hours']}h {metrics['minutes']}m {metrics['seconds']}s")
                    print(f"Point-to-point driving distance: {metrics['total_distance'] / 1000:.1f} km ({metrics['total_distance'] / 1609.34:.3f} miles)")
                    print(f"Point-to-point average driving speed: {metrics['average_kph']:.2f} kph ({metrics['average_mph']:.2f} mph)")

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