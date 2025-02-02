import json
import googlemaps
import keys
from datetime import datetime
from typing import Dict, Any


def calculate_speed(distance: float, duration: float) -> tuple:
    """Calculate speed in kph and mph."""
    kph = (distance / 1000) / (duration / 3600)
    mph = (distance / 1609.34) / (duration / 3600)
    return kph, mph

def calculate_route_metrics(route: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate metrics for a route."""
    total_duration = sum(leg.get('duration', {}).get('value', 0) for leg in route.get('legs', []))
    total_distance = sum(leg.get('distance', {}).get('value', 0) for leg in route.get('legs', []))
    average_kph, average_mph = calculate_speed(total_distance, total_duration)
    
    hours, remainder = divmod(total_duration, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return {
        'total_duration': total_duration,
        'total_distance': total_distance,
        'average_kph': average_kph,
        'average_mph': average_mph,
        'hours': hours,
        'minutes': minutes,
        'seconds': seconds
    }

def process_route(gmaps: googlemaps.Client, route_data: Dict[str, Any]) -> None:
    """Process a single route and calculate its metrics."""
    try:
        print(f"\nProcessing route: {route_data.get('route_name', 'Unnamed Route')}")
        print(f"Description: {route_data.get('route_description', 'No description available')}")
        
        waypoints = route_data.get('waypoints', [])
        place_ids = [wp.get('place_id') for wp in waypoints if wp.get('place_id')]
        
        if not place_ids:
            print("No place IDs found in route")
            return
        
        origin = place_ids[0]
        destination = place_ids[-1]
        waypoint_ids = [f"place_id:{pid}" for pid in place_ids[1:-1]]

        # Calculate routes for different modes
        modes = ['driving', 'bicycling', 'walking', 'transit']
        route_results = {}
        for mode in modes:
            result = gmaps.directions(
                f"place_id:{origin}",
                f"place_id:{destination}",
                waypoints=waypoint_ids if mode == 'driving' else None,
                mode=mode,
                departure_time=datetime.now()
            )
            route_results[mode] = result[0] if result else None

        print("\n=== Route Summary ===")
        for mode, route in route_results.items():
            if route:
                metrics = calculate_route_metrics(route)
                print(f"\nMode: {mode.capitalize()}")
                print(f"Total time: {metrics['hours']} hours, {metrics['minutes']} minutes, {metrics['seconds']} seconds")
                print(f"Total time in seconds: {metrics['total_duration']} seconds")
                print(f"Total distance: {metrics['total_distance'] / 1000:.1f} km ({metrics['total_distance'] / 1609.34:.3f} miles)")
                print(f"Average speed: {metrics['average_kph']:.2f} kph ({metrics['average_mph']:.2f} mph)")
            else:
                print(f"\nNo {mode} route found")

        print("\n=== Point-to-Point Summary ===")
        point_to_point_result = gmaps.directions(
            f"place_id:{origin}",
            f"place_id:{destination}",
            mode="driving",
            departure_time=datetime.now()
        )

        if point_to_point_result:
            point_to_point_route = point_to_point_result[0]
            metrics = calculate_route_metrics(point_to_point_route)
            print(f"Point-to-point driving time: {metrics['hours']} hours, {metrics['minutes']} minutes, {metrics['seconds']} seconds")
            print(f"Point-to-point driving distance: {metrics['total_distance'] / 1000:.1f} km ({metrics['total_distance'] / 1609.34:.3f} miles)")
            print(f"Point-to-point average driving speed: {metrics['average_kph']:.2f} kph ({metrics['average_mph']:.2f} mph)")
        else:
            print("No point-to-point route found")

        print("\n=== Detailed Route ===")
        for mode, route in route_results.items():
            if route:
                print(f"\nMode: {mode.capitalize()}")
                for i, leg in enumerate(route.get('legs', []), 1):
                    leg_distance = leg.get('distance', {}).get('value', 0)
                    leg_duration = leg.get('duration', {}).get('value', 0)
                    print(f"\nLeg {i}:")
                    print(f"From: {leg.get('start_address', 'Unknown')}")
                    print(f"To: {leg.get('end_address', 'Unknown')}")
                    print(f"Time: {leg.get('duration', {}).get('text', 'Unknown')}")
                    print(f"Time in seconds: {leg_duration} seconds")
                    print(f"Distance: {leg.get('distance', {}).get('text', 'Unknown')} ({leg_distance / 1609.34:.3f} miles)")
                    if mode != 'transit':
                        leg_kph, leg_mph = calculate_speed(leg_distance, leg_duration)
                        print(f"Speed: {leg_kph:.2f} kph ({leg_mph:.2f} mph)")

    except Exception as e:
        print(f"Error processing route: {str(e)}")

def main() -> None:
    """Main function to process all routes."""
    # Load environment variables    
    api_key = keys.get_google_maps_api_key()
    if not api_key:
        raise ValueError("GOOGLE_MAPS_API_KEY environment variable is not set")

    # Initialize Google Maps client
    try:
        gmaps = googlemaps.Client(key=api_key)
        
        # Read the routes file
        try:
            with open('routes_enriched.json', 'r') as f:
                routes_data = json.load(f)
        except FileNotFoundError:
            print("Error: routes_enriched.json file not found")
            return
        except json.JSONDecodeError:
            print("Error: Invalid JSON format in routes_enriched.json")
            return
        except Exception as e:
            print(f"Error reading file: {str(e)}")
            return
        
        # Process each route
        for route in routes_data.get('routes', []):
            process_route(gmaps, route)
            
    except Exception as e:
        if isinstance(e, ValueError) and "API key" in str(e):
            raise
        print(f"Error in main: {str(e)}")
        return

if __name__ == "__main__":
    main()