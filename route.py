import os
import json
import googlemaps
from datetime import datetime
from dotenv import load_dotenv

def process_route(gmaps, route_data):
    """Process a single route and calculate its metrics."""
    print(f"\nProcessing route: {route_data['route_name']}")
    print(f"Description: {route_data['route_description']}")
    
    # Get place IDs from the waypoints
    place_ids = [wp['place_id'] for wp in route_data['waypoints']]
    
    if not place_ids:
        print("No place IDs found in route")
        return
    
    # Calculate route using these place IDs
    origin = place_ids[0]
    destination = place_ids[-1]
    waypoints = [f"place_id:{pid}" for pid in place_ids[1:-1]]

    directions_result = gmaps.directions(
        f"place_id:{origin}",
        f"place_id:{destination}",
        waypoints=waypoints,
        mode="driving",
        departure_time=datetime.now()
    )

    if directions_result:
        route = directions_result[0]
        total_duration = sum(leg['duration']['value'] for leg in route['legs'])
        
        # Convert seconds to hours, minutes, and seconds
        hours, remainder = divmod(total_duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        total_distance = sum(leg['distance']['value'] for leg in route['legs'])
        
        print("\n=== Route Summary ===")
        print(f"Total trip time: {hours} hours, {minutes} minutes, {seconds} seconds")
        print(f"Total trip time in seconds: {total_duration} seconds")
        print(f"Total distance: {total_distance / 1000:.1f} km ({total_distance / 1609.34:.3f} miles)")
        
        print("\n=== Detailed Route ===")
        for i, leg in enumerate(route['legs']):
            leg_distance_miles = float(leg['distance']['value']) / 1609.34
            print(f"\nLeg {i+1}:")
            print(f"From: {leg['start_address']}")
            print(f"To: {leg['end_address']}")
            print(f"Time: {leg['duration']['text']}")
            print(f"Time in seconds: {leg['duration']['value']} seconds")
            print(f"Distance: {leg['distance']['text']} ({leg_distance_miles:.3f} miles)")

def main():
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        raise ValueError("GOOGLE_MAPS_API_KEY environment variable is not set")

    # Initialize Google Maps client
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
    
    # Process each route
    for route in routes_data['routes']:
        process_route(gmaps, route)

if __name__ == "__main__":
    main()