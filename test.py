import os
import googlemaps
from datetime import datetime
import json

# Get API key from environment variable
api_key = os.getenv('GOOGLE_MAPS_API_KEY')

if not api_key:
    raise ValueError("GOOGLE_MAPS_API_KEY environment variable is not set")

gmaps = googlemaps.Client(key=api_key)

# Geocoding an address
print("\n=== Geocoding Result ===")
geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')
print(json.dumps(geocode_result, indent=2))

# Look up an address with reverse geocoding
print("\n=== Reverse Geocoding Result ===")
reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))
print(json.dumps(reverse_geocode_result, indent=2))

# Request directions via public transit
print("\n=== Directions Result ===")
now = datetime.now()
directions_result = gmaps.directions("Sydney Town Hall",
                                   "Parramatta, NSW",
                                   mode="transit",
                                   departure_time=now)
print(json.dumps(directions_result, indent=2))

# Validate an address with address validation
print("\n=== Address Validation Result ===")
addressvalidation_result = gmaps.addressvalidation(['1600 Amphitheatre Pk'], 
                                                 regionCode='US',
                                                 locality='Mountain View', 
                                                 enableUspsCass=True)
print(json.dumps(addressvalidation_result, indent=2))

# Simple reverse geocode
print("\n=== Second Reverse Geocoding Result ===")
address_descriptor_result = gmaps.reverse_geocode((40.714224, -73.961452))
print(json.dumps(address_descriptor_result, indent=2))