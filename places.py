import os
import googlemaps
from datetime import datetime
import json

api_key = os.getenv('GOOGLE_MAPS_API_KEY')
if not api_key:
    raise ValueError("GOOGLE_MAPS_API_KEY environment variable is not set")

gmaps = googlemaps.Client(key=api_key)

# First let's find place IDs for some Alameda locations
locations = [
    "South Shore Center, Alameda, CA",
    "Crown Memorial State Beach, Alameda, CA",
    "USS Hornet Museum, Alameda, CA",
    "Alameda Point, Alameda, CA"
]

print("Finding place IDs for locations:")
for location in locations:
    result = gmaps.find_place(
        location,
        'textquery',
        fields=['place_id', 'formatted_address', 'name']
    )
    if result['candidates']:
        print(f"\n{location}:")
        print(f"Place ID: {result['candidates'][0]['place_id']}")

# Once we have the place IDs, we can use them in our directions request