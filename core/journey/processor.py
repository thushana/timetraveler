# Standard Library
import json
import re
import urllib.parse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Third-party
import googlemaps

# Application
from core.config import settings

logger = logging.getLogger(__name__)

class JourneyProcessor:
    def __init__(
        self,
        gmaps_client: googlemaps.Client,
        debug: bool = None
    ):
        """Initialize processor with a Google Maps client instance.
        
        Args:
            gmaps_client: Configured Google Maps client instance
            debug: Optional override for debug mode (default from settings)
        """
        self.gmaps = gmaps_client
        self.debug = debug if debug is not None else settings.DEBUG
    
    def extract_plus_codes(self, url: str) -> List[Dict[str, str]]:
        """Extract Plus Codes and their locations from Google Maps URL."""
        decoded_url = urllib.parse.unquote(url)
        matches = re.findall(r'!2s([A-Z0-9]{4,6}\+[A-Z0-9]{2,3}),\+([^!]+)', decoded_url)
        if not matches:
            raise ValueError("No Plus Codes found in the URL")
        return [{'plus_code': code, 'location': location} for code, location in matches]

    def enrich_waypoint_data(self, plus_code_with_location: Dict[str, str]) -> Dict[str, Any]:
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

    def process_route(self, maps_url: str, journey_name: str) -> Dict[str, Any]:
        """Process entire journey and create JSON output."""
        if self.debug:
            logger.info(f"Processing journey: {journey_name}")
            
        # Extract Plus Codes
        waypoints = self.extract_plus_codes(maps_url)
        
        # Enrich each waypoint with place details
        enriched_waypoints = []
        for waypoint in waypoints:
            try:
                enriched_data = self.enrich_waypoint_data(waypoint)
                enriched_waypoints.append(enriched_data)
            except Exception as e:
                logger.error(f"Error processing waypoint {waypoint}: {str(e)}")
                continue

        # Create journey data structure
        journey_data = {
            'journey_name': journey_name,
            'created_at': datetime.now().isoformat(),
            'waypoints': enriched_waypoints,
            'original_url': maps_url
        }
        
        if self.debug:
            logger.info(f"Completed processing journey: {journey_name}")
            
        return journey_data

    def process_routes_file(
        self,
        journeys_filename: Path = None,
        output_filename: Path = None
    ) -> Dict[str, Any]:
        """Process all journeys from journeys.json and create enriched version."""
        journeys_filename = journeys_filename or settings.RAW_JOURNEYS_PATH
        output_filename = output_filename or settings.PROCESSED_JOURNEYS_PATH

        if self.debug:
            logger.info(f"Processing journeys from {journeys_filename}")
            logger.info(f"Output will be saved to {output_filename}")

        try:
            # Ensure output directory exists
            output_filename.parent.mkdir(parents=True, exist_ok=True)
            
            # Load journeys file
            if not journeys_filename.exists():
                raise FileNotFoundError(f"Journeys file not found: {journeys_filename}")
                
            with journeys_filename.open('r', encoding='utf-8') as f:
                journeys_data = json.load(f)
            
            # Create enriched journeys data structure
            enriched_data = {
                "journeys": []
            }
            
            # Process each journey
            for journey in journeys_data.get("journeys", []):
                try:
                    if self.debug:
                        logger.info(f"\nProcessing journey: {journey['journey_name']}")
                    
                    # Process the journey and get enriched data
                    journey_data = self.process_route(journey['journey_url'], journey['journey_name'])
                    
                    # Add additional fields from original journey data
                    journey_data['journey_description'] = journey.get('journey_description', '')
                    
                    enriched_data["journeys"].append(journey_data)
                    
                except Exception as e:
                    logger.error(f"Error processing journey '{journey['journey_name']}': {str(e)}")
                    continue
            
            # Save enriched data
            try:
                with output_filename.open('w', encoding='utf-8') as f:
                    json.dump(enriched_data, f, indent=2, ensure_ascii=False)
                if self.debug:
                    logger.info(f"Enriched journey data saved to {output_filename}")
            except IOError as e:
                raise IOError(f"Error saving enriched journey data to {output_filename}: {str(e)}")
            
            return enriched_data
        
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in journeys file {journeys_filename}")

    def print_routes_summary(self, journeys_data: Dict[str, Any]) -> None:
        """Print a formatted summary of all journeys."""
        print("\nRoutes summary:")
        print(f"Total journeys: {len(journeys_data['journeys'])}")
        
        for journey in journeys_data['journeys']:
            print(f"\nRoute: {journey['journey_name']}")
            print(f"Description: {journey.get('journey_description', 'No description')}")
            print(f"Created at: {journey['created_at']}")
            print(f"Number of waypoints: {len(journey['waypoints'])}")
            
            print("\nWaypoints:")
            for i, waypoint in enumerate(journey['waypoints'], 1):
                print(f"\n  {i}. {waypoint['formatted_address']}")
                print(f"     Plus Code: {waypoint['plus_code']}")
                print(f"     Coordinates: ({waypoint['latitude']}, {waypoint['longitude']})")

    def print_json(self, journey_data: Dict[str, Any]) -> None:
        """Print the journey data as formatted JSON."""
        print("\nJSON Output:")
        print(json.dumps(journey_data, indent=2, ensure_ascii=False))