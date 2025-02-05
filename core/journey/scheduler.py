import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, cast

import googlemaps
from sqlalchemy import Column, and_
from sqlalchemy.orm import Session

from core.config import settings
from core.journey.calculator import JourneyMetricsCalculator
from core.journey.processor import JourneyProcessor
from core.journey.reporter import JourneyReporter
from database.models.day_of_week import DayOfWeek
from database.models.journey import Journey
from database.models.journey_leg import JourneyLeg
from database.models.journey_measurement import JourneyMeasurement
from database.models.time_slot import TimeSlot
from database.models.transit_mode import TransitMode
from database.session import get_db

logger = logging.getLogger(__name__)


class JourneyScheduler:
    def __init__(self, max_workers: Optional[int] = None, debug: Optional[bool] = None):
        self.max_workers = max_workers if max_workers is not None else settings.MAX_WORKERS
        self.debug = debug if debug is not None else settings.DEBUG
        self.completed_routes: List[Dict[str, Any]] = []

        api_key = settings.get_google_maps_api_key()
        self.gmaps = googlemaps.Client(key=api_key)

        self.calculator = JourneyMetricsCalculator(self.gmaps, max_workers=self.max_workers, debug=self.debug)
        self.reporter = JourneyReporter(debug=self.debug)

    def load_active_journeys(self, db: Session) -> List[Journey]:
        active_journeys = (
            db.query(Journey)
            .filter(
                and_(
                    Journey.status_id == 1,  # Active status
                    Journey.waypoints.any(),  # Has waypoints
                )
            )
            .all()
        )

        if not active_journeys:
            logger.warning("No active journeys found")

        if self.debug:
            logger.info(f"Loaded {len(active_journeys)} active journeys")

        return active_journeys

    def get_transit_mode_id(self, db: Session, mode: str) -> int:
        mode_key = mode.lower()
        if mode_key == "driving_routed":
            mode_key = "driving"

        mode_record = db.query(TransitMode).filter(TransitMode.mode == mode_key).first()
        if not mode_record:
            logger.warning(f"Transit mode {mode_key} not found, using default mode 'driving'")
            mode_record = db.query(TransitMode).filter(TransitMode.mode == "driving").first()

        return int(mode_record.id) if mode_record else 1

    def get_time_slot_id(self, db: Session, dt: datetime) -> int:
        hour = dt.hour
        minute = (dt.minute // 15) * 15
        slot_key = f"{hour:02d}{minute:02d}"

        if hour < 4:
            period = "overnight"
        elif hour < 8:
            period = "dawn"
        elif hour < 12:
            period = "morning"
        elif hour < 16:
            period = "afternoon"
        elif hour < 20:
            period = "evening"
        else:
            period = "night"

        slot_key = f"{slot_key}_{period}"
        slot = db.query(TimeSlot).filter(TimeSlot.slot == slot_key).first()
        if not slot:
            logger.warning(f"Time slot {slot_key} not found, using id 1")
            return 1
        return int(slot.id)

    def get_waypoint_id(self, journey: Journey, address: str) -> int:
        for wp in journey.waypoints:
            if wp.formatted_address == address:
                return wp.id
        return journey.waypoints[0].id  # Fallback to first waypoint

    def save_journey_metrics(self, db: Session, journey: Journey, metrics: Dict[str, Any]) -> None:
        try:
            now = datetime.now()

            for mode, mode_data in metrics["modes"].items():
                transit_mode_id = self.get_transit_mode_id(db, mode)
                existing = (
                    db.query(JourneyMeasurement)
                    .filter(
                        JourneyMeasurement.journey_id == journey.id,
                        JourneyMeasurement.transit_mode_id == transit_mode_id,
                    )
                    .first()
                )

                if existing:
                    existing.timestamp = cast(Column[datetime], now)
                    existing.local_timestamp = cast(Column[datetime], now)
                    existing.duration_seconds = mode_data["metrics"]["duration_seconds"]
                    existing.distance_meters = mode_data["metrics"]["distance_meters"]
                    existing.speed_kph = mode_data["metrics"]["speed_kph"]
                    existing.raw_response = mode_data
                else:
                    measurement = JourneyMeasurement(
                        journey_id=journey.id,
                        transit_mode_id=transit_mode_id,
                        timestamp=now,
                        local_timestamp=now,
                        day_of_week_id=now.isoweekday(),
                        time_slot_id=self.get_time_slot_id(db, now),
                        duration_seconds=mode_data["metrics"]["duration_seconds"],
                        distance_meters=mode_data["metrics"]["distance_meters"],
                        speed_kph=mode_data["metrics"]["speed_kph"],
                        raw_response=mode_data,
                        created_at=now,
                    )
                    db.add(measurement)

                db.flush()

                if "leg_details" in mode_data:
                    for seq, leg in enumerate(mode_data["leg_details"], 1):
                        existing_leg = (
                            db.query(JourneyLeg)
                            .filter_by(
                                journey_measurement_id=(existing.id if existing else measurement.id),
                                sequence_number=seq,
                            )
                            .first()
                        )

                        if not existing_leg:
                            journey_leg = JourneyLeg(
                                journey_measurement_id=(existing.id if existing else measurement.id),
                                sequence_number=seq,
                                start_waypoint_id=self.get_waypoint_id(journey, leg["start_address"]),
                                end_waypoint_id=self.get_waypoint_id(journey, leg["end_address"]),
                                duration_seconds=leg["duration_seconds"],
                                distance_meters=leg["distance_meters"],
                                speed_kph=leg["speed_kph"],
                                created_at=now,
                            )
                            db.add(journey_leg)

            db.commit()
            logger.info(f"Saved all metrics for journey '{journey.name}'")

        except Exception as e:
            db.rollback()
            logger.error(f"Error saving metrics: {str(e)}")
            raise

    def process_single_journey(self, db: Session, journey: Journey) -> None:
        try:
            logger.info(f"Processing journey: {journey.name}")
            metrics = self.calculator.process_route(journey)
            self.save_journey_metrics(db, journey, metrics)
            self.completed_routes.append(metrics)
            logger.info(f"Completed processing journey: {journey.name}")
        except Exception as e:
            logger.error(f"Error processing journey '{journey.name}': {str(e)}")
            raise

    def process_all_journeys(self) -> None:
        start_time = datetime.now()

        with get_db() as db:
            try:
                journeys = self.load_active_journeys(db)
                total_journeys = len(journeys)
                logger.info(f"Processing {total_journeys} journeys")

                with self.calculator:
                    for journey in journeys:
                        self.process_single_journey(db, journey)

                self.reporter.print_batch_summary(db, journeys)

                processing_time = (datetime.now() - start_time).total_seconds() * 1000
                logger.info(f"Completed in {processing_time:.2f}ms")

                if total_journeys > 0:
                    logger.info(f"Average: {processing_time / total_journeys:.2f}ms per journey")

            except Exception as e:
                logger.error(f"Error in process_all_journeys: {str(e)}")
                raise
