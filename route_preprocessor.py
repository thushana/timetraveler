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

    def process_routes_file(self, routes_filename="routes.json", output_filename="routes_enriched.json"):
        """Process all routes from routes.json and create enriched version."""
        try:
            # Load routes file
            with open(routes_filename, 'r', encoding='utf-8') as f:
                routes_data = json.load(f)
            
            # Create enriched routes data structure
            enriched_data = {
                "routes": []
            }
            
            # Process each route
            for route in routes_data.get("routes", []):
                try:
                    print(f"\nProcessing route: {route['route_name']}")
                    
                    # Process the route and get enriched data
                    route_data = self.process_route(route['route_url'], route['route_name'])
                    
                    # Add additional fields from original route data
                    route_data['route_description'] = route.get('route_description', '')
                    
                    enriched_data["routes"].append(route_data)
                    
                except Exception as e:
                    print(f"Error processing route '{route['route_name']}': {str(e)}")
                    continue
            
            # Save enriched data
            try:
                with open(output_filename, 'w', encoding='utf-8') as f:
                    json.dump(enriched_data, f, indent=2, ensure_ascii=False)
                print(f"\nEnriched route data saved to {output_filename}")
            except IOError as e:
                raise IOError(f"Error saving enriched route data to {output_filename}: {str(e)}")
            
            return enriched_data
        
        except FileNotFoundError:
            raise FileNotFoundError(f"Routes file {routes_filename} not found")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in routes file {routes_filename}")

    def print_routes_summary(self, routes_data):
        """Print a formatted summary of all routes."""
        print("\nRoutes summary:")
        print(f"Total routes: {len(routes_data['routes'])}")
        
        for route in routes_data['routes']:
            print(f"\nRoute: {route['route_name']}")
            print(f"Description: {route.get('route_description', 'No description')}")
            print(f"Created at: {route['created_at']}")
            print(f"Number of waypoints: {len(route['waypoints'])}")
            
            print("\nWaypoints:")
            for i, waypoint in enumerate(route['waypoints'], 1):
                print(f"\n  {i}. {waypoint['formatted_address']}")
                print(f"     Plus Code: {waypoint['plus_code']}")
                print(f"     Coordinates: ({waypoint['latitude']}, {waypoint['longitude']})")

    def print_json(self, route_data):
        """Print the route data as formatted JSON."""
        print("\nJSON Output:")
        print(json.dumps(route_data, indent=2, ensure_ascii=False))

def main():
    if len(sys.argv) < 2:
        print("Usage: python route_preprocessor.py [--json]")
        sys.exit(1)

    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        raise ValueError("GOOGLE_MAPS_API_KEY environment variable is not set")

    show_json = "--json" in sys.argv

    processor = RoutePreProcessor(api_key)
    
    try:
        # Process all routes
        enriched_data = processor.process_routes_file()
        
        # Print output
        if show_json:
            processor.print_json(enriched_data)
        else:
            processor.print_routes_summary(enriched_data)
        
    except Exception as e:
        print(f"Error processing routes: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()