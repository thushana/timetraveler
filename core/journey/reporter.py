import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from core.config import settings
from database.models.journey import Journey
from database.models.journey_leg import JourneyLeg
from database.models.journey_measurement import JourneyMeasurement
from database.models.transit_mode import TransitMode

logger = logging.getLogger(__name__)


class JourneyReporter:
    def __init__(self, debug: Optional[bool] = None):
        self.debug = debug if debug is not None else settings.DEBUG

    @staticmethod
    def format_duration(seconds: int) -> str:
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"

    @staticmethod
    def meters_to_miles(meters: float) -> float:
        return meters / 1609.34

    @staticmethod
    def kph_to_mph(kph: float) -> float:
        return kph * 0.621371

    @staticmethod
    def get_mode_emoji(mode: str) -> str:
        emoji_map = {
            "driving": "🚗",
            "driving_routed": "🚙",
            "bicycling": "🚲",
            "walking": "🚶",
            "transit": "🚌",
        }
        return emoji_map.get(mode, "🗺️")

    def print_measurement_details(self, db: Session, measurement: JourneyMeasurement, indent: str = "") -> None:
        """Print details for a specific journey measurement."""
        if not measurement:
            if self.debug:
                logger.warning("No measurement data found")
            return

        # Fetch the transit mode name using the provided db session
        mode_record = db.query(TransitMode).filter_by(id=measurement.transit_mode_id).first()
        mode = str(mode_record.mode) if mode_record else "unknown"

        emoji = self.get_mode_emoji(mode)
        print(f"\n{indent}{emoji} {mode.upper()}:")
        print(f"{indent}Duration: {self.format_duration(int(measurement.duration_seconds))}")
        print(
            f"{indent}Distance: {float(measurement.distance_meters)/1000:.1f} km ({self.meters_to_miles(float(measurement.distance_meters)):.1f} miles)"
        )
        print(
            f"{indent}Average Speed: {float(measurement.speed_kph):.1f} kph ({self.kph_to_mph(float(measurement.speed_kph)):.1f} mph)"
        )

        if measurement.legs:
            if self.debug:
                logger.info(f"Printing {len(measurement.legs)} legs for {mode}")

            print(f"\n{indent}Detailed Leg Information:")
            for i, leg in enumerate(measurement.legs, 1):
                print(f"\n{indent}🔸 Leg {i}:")
                print(f"{indent}From: {leg.start_waypoint.formatted_address}")
                print(f"{indent}To: {leg.end_waypoint.formatted_address}")
                print(f"{indent}Duration: {self.format_duration(leg.duration_seconds)}")
                print(
                    f"{indent}Distance: {float(leg.distance_meters)/1000:.1f} km ({self.meters_to_miles(float(leg.distance_meters)):.1f} miles)"
                )
                print(
                    f"{indent}Speed: {float(leg.speed_kph):.1f} kph ({self.kph_to_mph(float(leg.speed_kph)):.1f} mph)"
                )

    def print_journey_summary(self, db: Session, journey: Journey, measurements: List[JourneyMeasurement]) -> None:
        """Print a detailed summary of journey measurements including imperial conversions."""
        if self.debug:
            logger.info(f"Printing summary for journey: {journey.name}")

        print("\n" + "=" * 80)
        print(f"Journey: {journey.name}")
        print(f"Description: {journey.description or 'No description available'}")
        print("=" * 80)

        print("\n📍 DIRECT ROUTES:")
        print("-" * 40)

        for measurement in measurements:
            if not measurement.transit_mode_id == 2:  # Skip driving_routed
                self.print_measurement_details(db, measurement)

        # Print driving_routed separately
        routed_measurement = next((m for m in measurements if m.transit_mode_id == 2), None)
        if routed_measurement:
            print("\n" + "=" * 80)
            print("🛣️ DRIVING (ROUTED WITH WAYPOINTS):")
            print("-" * 40)
            self.print_measurement_details(db, measurement)

        print("\n" + "=" * 80)

    def print_batch_summary(self, db: Session, completed_journeys: List[Journey]) -> None:
        """Print summaries for a batch of completed journeys."""
        if not completed_journeys:
            logger.warning("No journeys to summarize")
            return

        if self.debug:
            logger.info(f"Printing summaries for {len(completed_journeys)} journeys")

        for journey in completed_journeys:
            measurements = journey.measurements
            self.print_journey_summary(db, journey, measurements)
