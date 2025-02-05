from datetime import datetime
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import logging
import googlemaps

from core.config import settings
from database.models.journey import Journey
from database.models.journey_measurement import JourneyMeasurement
from database.models.journey_leg import JourneyLeg

logger = logging.getLogger(__name__)

@dataclass
class JourneyTask:
    origin: str
    destination: str
    waypoint_ids: List[str]
    mode: str
    departure_time: datetime
    is_routed: bool
    journey: Journey

class JourneyMetricsCalculator:
    def __init__(
        self,
        gmaps_client: googlemaps.Client,
        max_workers: int = None,
        debug: bool = None
    ):
        self.gmaps = gmaps_client
        self.max_workers = max_workers if max_workers is not None else settings.MAX_WORKERS
        self.debug = debug if debug is not None else settings.DEBUG
        self._executor = None
        
    @property
    def thread_pool(self):
        if self._executor is None:
            self._executor = ThreadPoolExecutor(max_workers=self.max_workers)
        return self._executor

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._executor:
            self._executor.shutdown(wait=True)
            self._executor = None

    @staticmethod
    def calculate_speed(distance_meters: float, duration_seconds: float) -> float:
        if duration_seconds <= 0:
            return 0.0
        return (distance_meters / 1000) / (duration_seconds / 3600)

    def create_route_tasks(self, journey: Journey) -> List[JourneyTask]:
        tasks = []
        waypoints = journey.waypoints
        place_ids = [wp.place_id for wp in waypoints if wp.place_id]
        
        if not place_ids:
            return tasks

        origin = f"place_id:{place_ids[0]}"
        destination = f"place_id:{place_ids[-1]}"
        waypoint_ids = [f"place_id:{pid}" for pid in place_ids[1:-1]]
        departure_time = datetime.now()

        modes = ['driving', 'bicycling', 'walking', 'transit']
        
        for mode in modes:
            tasks.append(JourneyTask(
                origin=origin,
                destination=destination,
                waypoint_ids=[],
                mode=mode,
                departure_time=departure_time,
                is_routed=False,
                journey=journey
            ))

            if mode == 'driving' and waypoint_ids:
                tasks.append(JourneyTask(
                    origin=origin,
                    destination=destination,
                    waypoint_ids=waypoint_ids,
                    mode=mode,
                    departure_time=departure_time,
                    is_routed=True,
                    journey=journey
                ))

        return tasks

    def process_task(self, task: JourneyTask) -> Optional[Dict[str, Any]]:
        try:
            if self.debug:
                logger.info(f"Processing {task.mode} {'(routed)' if task.is_routed else '(direct)'} "
                          f"for journey: {task.journey.name}")

            directions_kwargs = {
                'origin': task.origin,
                'destination': task.destination,
                'mode': task.mode,
                'departure_time': task.departure_time,
                'units': 'metric'
            }

            if task.is_routed and task.waypoint_ids:
                directions_kwargs['waypoints'] = task.waypoint_ids

            result = self.gmaps.directions(**directions_kwargs)
            
            if not result:
                if self.debug:
                    logger.warning(f"No journey found for {task.mode}")
                return None

            journey_metrics = self.calculate_route_metrics(result[0])
            if self.debug:
                logger.info(f"Calculated metrics for {task.mode}: {journey_metrics}")
            return journey_metrics

        except Exception as e:
            logger.error(f"Error processing task: {str(e)}")
            return {'error': str(e)}

    def calculate_route_metrics(self, journey: Dict[str, Any]) -> Dict[str, Any]:
        legs = journey.get('legs', [])
        total_duration = sum(leg.get('duration', {}).get('value', 0) for leg in legs)
        total_distance = sum(leg.get('distance', {}).get('value', 0) for leg in legs)
        
        leg_details = self.get_route_leg_details(legs)
        
        return {
            'metrics': {
                'duration_seconds': total_duration,
                'distance_meters': total_distance,
                'speed_kph': self.calculate_speed(total_distance, total_duration)
            },
            'leg_details': leg_details
        }

    def get_route_leg_details(self, legs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        details = []
        for leg in legs:
            duration = leg.get('duration', {}).get('value', 0)
            distance = leg.get('distance', {}).get('value', 0)
            
            details.append({
                'start_address': leg.get('start_address'),
                'end_address': leg.get('end_address'),
                'duration_seconds': duration,
                'distance_meters': distance,
                'speed_kph': self.calculate_speed(distance, duration)
            })
        return details

    def process_route(self, journey: Journey) -> Dict[str, Any]:
        try:
            if self.debug:
                logger.info(f"Processing journey: {journey.name}")

            journey_metrics = {
                'journey_name': journey.name,
                'journey_description': journey.description or 'No description available',
                'timestamp': datetime.now().isoformat(),
                'modes': {},
                'status': 'success'
            }

            tasks = self.create_route_tasks(journey)
            if not tasks:
                journey_metrics['status'] = 'error'
                journey_metrics['error'] = 'No valid tasks created for journey'
                return journey_metrics

            futures = {
                self.thread_pool.submit(self.process_task, task): task 
                for task in tasks
            }

            for future in as_completed(futures):
                task = futures[future]
                try:
                    result = future.result()
                    if result:
                        mode_key = f"{task.mode}_routed" if task.is_routed else task.mode
                        journey_metrics['modes'][mode_key] = result
                        if self.debug:
                            logger.info(f"Added {mode_key} metrics to journey")
                except Exception as e:
                    logger.error(f"Error processing {task.mode} journey: {str(e)}")
                finally:
                    future.cancel()

            if self.debug:
                logger.info(f"Final journey_metrics: {journey_metrics}")
            return journey_metrics

        except Exception as e:
            logger.error(f"Error processing journey: {str(e)}")
            return {
                'journey_name': journey.name,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }