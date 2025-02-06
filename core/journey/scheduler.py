import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, cast

import googlemaps
from sqlalchemy import and_
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from core.config import settings
from core.journey.calculator import JourneyMetricsCalculator
from core.journey.reporter import JourneyReporter
from database.models.journey import Journey
from database.models.journey_leg import JourneyLeg
from database.models.journey_measurement import JourneyMeasurement
from database.models.time_slot import TimeSlot
from database.models.transit_mode import TransitMode
from database.models.waypoint import Waypoint
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
                    Journey.status_id == 1,
                    Journey.waypoints.any(),
                )
            )
            .all()
        )

        if not active_journeys:
            logger.warning("No active journeys found")

        if self.debug:
            logger.info(f"Loaded {len(active_journeys)} active journeys")

        return active_journeys

    def save_journey_metrics(self, db: Session, journey: Journey, metrics: Dict[str, Any]) -> None:
        try:
            now = datetime.now()

            for mode, mode_data in metrics["modes"].items():
                transit_mode_id = TransitMode.get_id(db, mode)

                measurement = JourneyMeasurement(
                    journey_id=journey.id,
                    transit_mode_id=transit_mode_id,
                    timestamp=now,
                    local_timestamp=now,
                    day_of_week_id=now.isoweekday(),
                    time_slot_id=TimeSlot.get_id(db, now),
                    duration_seconds=mode_data["metrics"]["duration_seconds"],
                    distance_meters=mode_data["metrics"]["distance_meters"],
                    speed_kph=mode_data["metrics"]["speed_kph"],
                    raw_response=mode_data,
                    created_at=now,
                )
                db.add(measurement)

            db.commit()
            logger.info(f"Inserted new measurement for journey '{journey.name}'")

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
