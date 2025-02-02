import os
import json
import googlemaps
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

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

        directions_result = gmaps.directions(
            f"place_id:{origin}",
            f"place_id:{destination}",
            waypoints=waypoint_ids,
            mode="driving",
            departure_time=datetime.now()
        )

        if not directions_result:
            print("No route found")
            return
            
        route = directions_result[0]
        total_duration = sum(leg.get('duration', {}).get('value', 0) for leg in route.get('legs', []))
        
        hours, remainder = divmod(total_duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        total_distance = sum(leg.get('distance', {}).get('value', 0) for leg in route.get('legs', []))
        
        print("\n=== Route Summary ===")
        print(f"Total trip time: {hours} hours, {minutes} minutes, {seconds} seconds")
        print(f"Total trip time in seconds: {total_duration} seconds")
        print(f"Total distance: {total_distance / 1000:.1f} km ({total_distance / 1609.34:.3f} miles)")
        
        print("\n=== Detailed Route ===")
        for i, leg in enumerate(route.get('legs', []), 1):
            leg_distance = leg.get('distance', {}).get('value', 0)
            leg_distance_miles = float(leg_distance) / 1609.34
            print(f"\nLeg {i}:")
            print(f"From: {leg.get('start_address', 'Unknown')}")
            print(f"To: {leg.get('end_address', 'Unknown')}")
            print(f"Time: {leg.get('duration', {}).get('text', 'Unknown')}")
            print(f"Time in seconds: {leg.get('duration', {}).get('value', 0)} seconds")
            print(f"Distance: {leg.get('distance', {}).get('text', 'Unknown')} ({leg_distance_miles:.3f} miles)")
    except Exception as e:
        print(f"Error processing route: {str(e)}")

def main() -> None:
    """Main function to process all routes."""
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
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