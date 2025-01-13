import os
import googlemaps
from datetime import datetime
import re
import urllib.parse
import json
import sys

class RoutePreProcessor:
    def __init__(self, api_key):
        self.gmaps = googlemaps.Client(key=api_key)
    
    def extract_plus_codes(self, url):
        """Extract Plus Codes and their locations from Google Maps URL."""
        decoded_url = urllib.parse.unquote(url)
        matches = re.findall(r'!2s([A-Z0-9]{4,6}\+[A-Z0-9]{2,3}),\+([^!]+)', decoded_url)
        if not matches:
            raise ValueError("No Plus Codes found in the URL")
        return [{'plus_code': code, 'location': location} for code, location in matches]

    def enrich_waypoint_data(self, plus_code_with_location):
        """Get place details for a Plus Code."""
        # First get the Plus Code location details to get accurate coordinates
        full_code = f"{plus_code_with_location['plus_code']} {plus_code_with_location['location']}"
        
        # Get coordinates for the Plus Code
        place_result = self.gmaps.find_place(
            full_code,
            'textquery',
            fields=['geometry']
        )
        
        if not place_result['candidates']:
            raise ValueError(f"Could not find coordinates for {full_code}")
        
        # Get the coordinates
        lat = place_result['candidates'][0]['geometry']['location']['lat']
        lng = place_result['candidates'][0]['geometry']['location']['lng']
        
        # Use reverse geocoding to get the actual place details
        reverse_geocode = self.gmaps.reverse_geocode((lat, lng))
        
        if not reverse_geocode:
            raise ValueError(f"Could not find place details for coordinates {lat}, {lng}")
        
        # Find the most specific result (usually the first one)
        place_details = reverse_geocode[0]
        
        return {
            'plus_code': plus_code_with_location['plus_code'],
            'place_id': place_details['place_id'],
            'formatted_address': place_details.get('formatted_address', ''),
            'latitude': lat,
            'longitude': lng
        }

    def process_route(self, maps_url, route_name):
        """Process entire route and create JSON output."""
        # Extract Plus Codes
        waypoints = self.extract_plus_codes(maps_url)
        
        # Enrich each waypoint with place details
        enriched_waypoints = []
        for waypoint in waypoints:
            try:
                enriched_data = self.enrich_waypoint_data(waypoint)
                enriched_waypoints.append(enriched_data)
            except Exception as e:
                print(f"Error processing waypoint {waypoint}: {str(e)}")
                continue

        # Create route data structure
        route_data = {
            'route_name': route_name,
            'created_at': datetime.now().isoformat(),
            'waypoints': enriched_waypoints,
            'original_url': maps_url
        }
        
        return route_data

    def save_route(self, route_data, filename=None):
        """Save route data to JSON file."""
        if filename is None:
            # Create filename from route name
            safe_name = re.sub(r'[^a-zA-Z0-9]', '_', route_data['route_name'].lower())
            filename = f"route_{safe_name}.json"
        
        # Create any necessary directories in the path
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(route_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise IOError(f"Error saving route data to {filename}: {str(e)}")
        
        return filename
    
    def print_route_summary(self, route_data):
        """Print a formatted summary of the route data."""
        print("\nRoute summary:")
        print(f"Route name: {route_data['route_name']}")
        print(f"Created at: {route_data['created_at']}")
        print(f"Number of waypoints: {len(route_data['waypoints'])}")
        
        print("\nWaypoints:")
        for i, waypoint in enumerate(route_data['waypoints'], 1):
            print(f"\n{i}. {waypoint['formatted_address']}")
            print(f"   Plus Code: {waypoint['plus_code']}")
            print(f"   Coordinates: ({waypoint['latitude']}, {waypoint['longitude']})")

    def print_json(self, route_data):
        """Print the route data as formatted JSON."""
        print("\nJSON Output:")
        print(json.dumps(route_data, indent=2, ensure_ascii=False))

def main():
    if len(sys.argv) < 3:
        print("Usage: python route_preprocessor.py <route_name> <google_maps_url> [--json]")
        sys.exit(1)

    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        raise ValueError("GOOGLE_MAPS_API_KEY environment variable is not set")

    route_name = sys.argv[1]
    maps_url = sys.argv[2]
    show_json = "--json" in sys.argv

    processor = RoutePreProcessor(api_key)
    
    try:
        print(f"Processing route: {route_name}")
        route_data = processor.process_route(maps_url, route_name)
        
        # Save the route data
        filename = processor.save_route(route_data)
        print(f"Route data saved to {filename}")
        
        if show_json:
            processor.print_json(route_data)
        else:
            processor.print_route_summary(route_data)
        
    except Exception as e:
        print(f"Error processing route: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()