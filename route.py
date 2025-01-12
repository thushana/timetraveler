import os
import googlemaps
from datetime import datetime
import re
import urllib.parse

api_key = os.getenv('GOOGLE_MAPS_API_KEY')
if not api_key:
    raise ValueError("GOOGLE_MAPS_API_KEY environment variable is not set")

gmaps = googlemaps.Client(key=api_key)

# URL from Google Maps
maps_url = "https://www.google.com/maps/place/Shoreline+Park/@37.7622754,-122.279488,14z/data=!4m44!1m37!4m36!1m6!1m2!1s0x808f80d8f2cf1595:0xdf3815440c2316a8!2sPPQR%2B8V,+Alameda,+CA!2m2!1d-122.2578125!2d37.7383125!1m6!1m2!1s0x808f80d8f2cf1595:0xa0535ce0470d94a0!2sQQ52%2B4G,+Alameda,+CA!2m2!1d-122.2486875!2d37.7578125!1m6!1m2!1s0x808f80d8f2cf1595:0xf8fd790e72f5df59!2sQP9G%2BHV,+Alameda,+CA!2m2!1d-122.2728125!2d37.7689375!1m6!1m2!1s0x808f80d8f2cf1595:0xec9c663130539b34!2sQPH9%2BX5,+Alameda,+CA!2m2!1d-122.2820625!2d37.7799375!1m6!1m2!1s0x808f80d8f2cf1595:0x1684cd7f70336f0a!2sQPQ9%2BGW,+Alameda,+CA!2m2!1d-122.2801875!2d37.7888125"

# Extract Plus Codes using regex
decoded_url = urllib.parse.unquote(maps_url)

# Extract plus codes and their locations
matches = re.findall(r'!2s([A-Z0-9]{4,6}\+[A-Z0-9]{2,3}),\+([^!]+)', decoded_url)

if not matches:
    raise ValueError("No Plus Codes found in the URL")

# Format plus codes with their locations
plus_codes = [f"{code} {location}" for code, location in matches]
print("Extracted Plus Codes with locations:", plus_codes)

# Get place IDs for these plus codes
place_ids = []
print("\nFinding place IDs for Plus Codes:")
for code in plus_codes:
    result = gmaps.find_place(
        code,
        'textquery',
        fields=['place_id', 'formatted_address', 'name']
    )
    if result['candidates']:
        place_id = result['candidates'][0]['place_id']
        place_ids.append(place_id)
        print(f"\n{code}:")
        print(f"Place ID: {place_id}")

# Calculate route using these place IDs
if place_ids:
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