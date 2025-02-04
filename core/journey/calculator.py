# Standard Library
from datetime import datetime
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import logging

# Third-party
import googlemaps

# Application
from core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class JourneyTask:
    origin: str
    destination: str
    waypoint_ids: List[str]
    mode: str
    departure_time: datetime
    is_routed: bool
    journey_name: str

class JourneyMetricsCalculator:
    def __init__(
        self,
        gmaps_client: googlemaps.Client,
        max_workers: int = None,
        debug: bool = None
    ):
        """Initialize calculator with a Google Maps client instance.
        
        Args:
            gmaps_client: Configured Google Maps client instance
            max_workers: Optional override for thread pool size (default from settings)
            debug: Optional override for debug mode (default from settings)
        """
        self.gmaps = gmaps_client
        self.max_workers = max_workers if max_workers is not None else settings.MAX_WORKERS
        self.debug = debug if debug is not None else settings.DEBUG
        self._executor = None  # Lazy initialization of thread pool
        
    @property
    def thread_pool(self):
        """Lazy initialization of thread pool to reduce memory footprint."""
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
        """Calculate speed in kilometers per hour."""
        if duration_seconds <= 0:
            return 0.0
        return (distance_meters / 1000) / (duration_seconds / 3600)

    def create_route_tasks(self, journey_data: Dict[str, Any]) -> List[JourneyTask]:
        """Create journey tasks for parallel processing."""
        tasks = []
        waypoints = journey_data.get('waypoints', [])
        place_ids = [wp.get('place_id') for wp in waypoints if wp.get('place_id')]
        
        if not place_ids:
            return tasks

        origin = f"place_id:{place_ids[0]}"
        destination = f"place_id:{place_ids[-1]}"
        waypoint_ids = [f"place_id:{pid}" for pid in place_ids[1:-1]]
        departure_time = datetime.now()
        journey_name = journey_data.get('journey_name', 'Unnamed Journey')

        # Create tasks for all modes
        modes = ['driving', 'bicycling', 'walking', 'transit']
        
        for mode in modes:
            # Direct journey task
            tasks.append(JourneyTask(
                origin=origin,
                destination=destination,
                waypoint_ids=[],
                mode=mode,
                departure_time=departure_time,
                is_routed=False,
                journey_name=journey_name
            ))

            # Add journeyd task only for driving mode with waypoints
            if mode == 'driving' and waypoint_ids:
                tasks.append(JourneyTask(
                    origin=origin,
                    destination=destination,
                    waypoint_ids=waypoint_ids,
                    mode=mode,
                    departure_time=departure_time,
                    is_routed=True,
                    journey_name=journey_name
                ))

        return tasks

    def process_task(self, task: JourneyTask) -> Optional[Dict[str, Any]]:
        """Process a single journey task."""
        try:
            if self.debug:
                logger.info(f"Processing {task.mode} {'(routed)' if task.is_routed else '(direct)'} "
                          f"for journey: {task.journey_name}")

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
                    logger.warning(f"No journey found for {task.mode} "
                                 f"{'(routed)' if task.is_routed else '(direct)'}")
                return None

            # Process only the first journey and clear result to free memory
            journey_metrics = self.calculate_route_metrics(result[0])
            if self.debug:
                logger.info(f"Calculated metrics for {task.mode}: {journey_metrics}")
            return journey_metrics

        except Exception as e:
            logger.error(f"Error processing task: {str(e)}")
            return {'error': str(e)}

    def calculate_route_metrics(self, journey: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate metrics for a journey."""
        legs = journey.get('legs', [])
        total_duration = sum(leg.get('duration', {}).get('value', 0) for leg in legs)
        total_distance = sum(leg.get('distance', {}).get('value', 0) for leg in legs)
        
        # Process legs first and clear them to free memory
        leg_details = self.get_route_leg_details(legs)
        
        return {
            'metrics': {  # Wrap in 'metrics' key as expected by reporter
                'duration_seconds': total_duration,
                'distance_meters': total_distance,
                'speed_kph': self.calculate_speed(total_distance, total_duration)
            },
            'leg_details': leg_details
        }

    def get_route_leg_details(self, legs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract leg details from journey legs."""
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

    def process_route(self, journey_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single journey with all its modes using the thread pool."""
        try:
            journey_name = journey_data.get('journey_name', 'Unnamed Journey')
            if self.debug:
                logger.info(f"Processing journey: {journey_name}")

            journey_metrics = {
                'journey_name': journey_name,
                'journey_description': journey_data.get('journey_description', 'No description available'),
                'timestamp': datetime.now().isoformat(),
                'modes': {},
                'status': 'success'
            }

            # Create and process tasks
            tasks = self.create_route_tasks(journey_data)
            if not tasks:
                journey_metrics['status'] = 'error'
                journey_metrics['error'] = 'No valid tasks created for journey'
                return journey_metrics

            # Process tasks in parallel
            futures = {
                self.thread_pool.submit(self.process_task, task): task 
                for task in tasks
            }

            # Process completed tasks and clear memory as we go
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
                    # Clear the future to free memory
                    future.cancel()

            if self.debug:
                logger.info(f"Final journey_metrics: {journey_metrics}")
            return journey_metrics

        except Exception as e:
            logger.error(f"Error processing journey: {str(e)}")
            return {
                'journey_name': journey_name,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }