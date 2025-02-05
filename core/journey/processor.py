import json
import logging
import re
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import googlemaps
import pytz
from sqlalchemy.orm import Session

from database.models.journey import Journey
from database.models.waypoint import Waypoint

logger = logging.getLogger(__name__)


class JourneyProcessor:
    def __init__(
        self, db: Session, gmaps_client: googlemaps.Client, debug: bool = None
    ):
        self.db = db
        self.gmaps = gmaps_client
        self.debug = debug if debug is not None else False

    def extract_plus_codes(self, url: str) -> List[Dict[str, str]]:
        decoded_url = urllib.parse.unquote(url)
        matches = re.findall(
            r"!2s([A-Z0-9]{4,6}\+[A-Z0-9]{2,3}),\+([^!]+)", decoded_url
        )
        if not matches:
            raise ValueError("No Plus Codes found in the URL")
        return [{"plus_code": code, "location": location} for code, location in matches]

    def enrich_waypoint_data(
        self, plus_code_with_location: Dict[str, str]
    ) -> Dict[str, Any]:
        full_code = f"{plus_code_with_location['plus_code']} {plus_code_with_location['location']}"

        place_result = self.gmaps.find_place(
            full_code, "textquery", fields=["geometry"]
        )

        if not place_result["candidates"]:
            raise ValueError(f"Could not find coordinates for {full_code}")

        lat = place_result["candidates"][0]["geometry"]["location"]["lat"]
        lng = place_result["candidates"][0]["geometry"]["location"]["lng"]

        # Get timezone from Google Maps API
        timezone_result = self.gmaps.timezone((lat, lng))
        if not timezone_result or "timeZoneId" not in timezone_result:
            raise ValueError(
                f"Could not determine timezone for coordinates {lat}, {lng}"
            )

        timezone_str = timezone_result["timeZoneId"]

        reverse_geocode = self.gmaps.reverse_geocode((lat, lng))

        if not reverse_geocode:
            raise ValueError(
                f"Could not find place details for coordinates {lat}, {lng}"
            )

        place_details = reverse_geocode[0]
        address_components = place_details.get("address_components", [])

        city = next(
            (
                comp["long_name"]
                for comp in address_components
                if "locality" in comp["types"]
            ),
            None,
        )
        state = next(
            (
                comp["long_name"]
                for comp in address_components
                if "administrative_area_level_1" in comp["types"]
            ),
            None,
        )
        country = next(
            (
                comp["long_name"]
                for comp in address_components
                if "country" in comp["types"]
            ),
            None,
        )

        return {
            "plus_code": plus_code_with_location["plus_code"],
            "place_id": place_details["place_id"],
            "formatted_address": place_details.get("formatted_address", ""),
            "latitude": lat,
            "longitude": lng,
            "city": city,
            "state": state,
            "country": country,
            "timezone": timezone_str,
        }

    def process_route(
        self, maps_url: str, journey_name: str, description: str = None
    ) -> Journey:
        if self.debug:
            logger.info(f"Processing journey: {journey_name}")

        waypoints_data = self.extract_plus_codes(maps_url)
        now = datetime.now(pytz.UTC)

        # Check if journey already exists
        existing_journey = self.db.query(Journey).filter_by(name=journey_name).first()

        if existing_journey:
            logger.info(f"Journey '{journey_name}' already exists. Updating details.")
            journey = existing_journey
            journey.description = description or journey.description
            journey.updated_at = now

            # Explicitly delete existing waypoints before adding new ones
            self.db.query(Waypoint).filter(Waypoint.journey_id == journey.id).delete(
                synchronize_session=False
            )
            self.db.flush()
        else:
            # Get first waypoint data for journey location
            first_waypoint = self.enrich_waypoint_data(waypoints_data[0])

            # Create new journey record
            journey = Journey(
                name=journey_name,
                description=description,
                maps_url=maps_url,
                created_at=now,
                updated_at=now,
                raw_data={"url": maps_url},
                status_id=1,
                city=first_waypoint["city"],
                state=first_waypoint["state"],
                country=first_waypoint["country"],
                timezone=first_waypoint["timezone"],
            )
            self.db.add(journey)

        # Process waypoints
        for idx, waypoint_data in enumerate(waypoints_data, 1):
            try:
                enriched_data = self.enrich_waypoint_data(waypoint_data)

                waypoint = Waypoint(
                    sequence_number=idx,
                    journey_id=journey.id,  # Ensure waypoint is linked to the journey
                    place_id=enriched_data["place_id"],
                    plus_code=enriched_data["plus_code"],
                    formatted_address=enriched_data["formatted_address"],
                    latitude=enriched_data["latitude"],
                    longitude=enriched_data["longitude"],
                    created_at=now,
                )
                journey.waypoints.append(waypoint)

            except Exception as e:
                logger.error(f"Error processing waypoint {waypoint_data}: {str(e)}")
                continue

        try:
            self.db.commit()
            if self.debug:
                logger.info(
                    f"Journey '{journey_name}' updated successfully in database."
                )
        except Exception as e:
            self.db.rollback()
            logger.error(f"Database error updating journey '{journey_name}': {str(e)}")
            raise

        return journey

    def process_routes_file(self, journeys_filename: Path = None) -> List[Journey]:
        if self.debug:
            logger.info(f"Processing journeys from {journeys_filename}")

        try:
            if not journeys_filename.exists():
                raise FileNotFoundError(f"Journeys file not found: {journeys_filename}")

            with journeys_filename.open("r", encoding="utf-8") as f:
                journeys_data = json.load(f)

            processed_journeys = []

            for journey in journeys_data.get("journeys", []):
                try:
                    if self.debug:
                        logger.info(f"\nProcessing journey: {journey['route_name']}")

                    processed_journey = self.process_route(
                        journey["route_url"],
                        journey["route_name"],
                        journey.get("route_description"),
                    )
                    processed_journeys.append(processed_journey)

                except Exception as e:
                    logger.error(
                        f"Error processing journey '{journey['route_name']}': {str(e)}"
                    )
                    continue

            return processed_journeys

        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in journeys file {journeys_filename}")

    def print_journey_summary(self, journey: Journey) -> None:
        print(f"\nRoute: {journey.name}")
        print(f"Description: {journey.description or 'No description'}")
        print(f"Location: {journey.city}, {journey.state}, {journey.country}")
        print(f"Timezone: {journey.timezone}")
        print(f"Created at: {journey.created_at}")
        print(f"Number of waypoints: {len(journey.waypoints)}")

        print("\nWaypoints:")
        for waypoint in sorted(journey.waypoints, key=lambda w: w.sequence_number):
            print(f"\n  {waypoint.sequence_number}. {waypoint.formatted_address}")
            print(f"     Plus Code: {waypoint.plus_code}")
            print(f"     Coordinates: ({waypoint.latitude}, {waypoint.longitude})")
