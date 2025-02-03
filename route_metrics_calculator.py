from datetime import datetime
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import logging
import gc

import googlemaps

logger = logging.getLogger(__name__)

@dataclass
class RouteTask:
    origin: str
    destination: str
    waypoint_ids: List[str]
    mode: str
    departure_time: datetime
    is_routed: bool
    route_name: str

class RouteMetricsCalculator:
    def __init__(self, gmaps_client: googlemaps.Client, max_workers: int = 4, debug: bool = False):
        """Initialize calculator with a single thread pool optimized for Heroku Eco dyno."""
        self.gmaps = gmaps_client
        self.max_workers = max_workers
        self.debug = debug
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
        gc.collect()  # Force garbage collection

    @staticmethod
    def calculate_speed(distance_meters: float, duration_seconds: float) -> float:
        """Calculate speed in kilometers per hour."""
        if duration_seconds <= 0:
            return 0.0
        return (distance_meters / 1000) / (duration_seconds / 3600)

    def create_route_tasks(self, route_data: Dict[str, Any]) -> List[RouteTask]:
        """Create route tasks for parallel processing."""
        tasks = []
        waypoints = route_data.get('waypoints', [])
        place_ids = [wp.get('place_id') for wp in waypoints if wp.get('place_id')]
        
        if not place_ids:
            return tasks

        origin = f"place_id:{place_ids[0]}"
        destination = f"place_id:{place_ids[-1]}"
        waypoint_ids = [f"place_id:{pid}" for pid in place_ids[1:-1]]
        departure_time = datetime.now()
        route_name = route_data.get('route_name', 'Unnamed Route')

        # Create tasks for all modes
        modes = ['driving', 'bicycling', 'walking', 'transit']
        
        for mode in modes:
            # Direct route task
            tasks.append(RouteTask(
                origin=origin,
                destination=destination,
                waypoint_ids=[],
                mode=mode,
                departure_time=departure_time,
                is_routed=False,
                route_name=route_name
            ))

            # Add routed task only for driving mode with waypoints
            if mode == 'driving' and waypoint_ids:
                tasks.append(RouteTask(
                    origin=origin,
                    destination=destination,
                    waypoint_ids=waypoint_ids,
                    mode=mode,
                    departure_time=departure_time,
                    is_routed=True,
                    route_name=route_name
                ))

        return tasks

    def process_task(self, task: RouteTask) -> Optional[Dict[str, Any]]:
        """Process a single route task."""
        try:
            if self.debug:
                logger.info(f"Processing {task.mode} {'(routed)' if task.is_routed else '(direct)'} "
                          f"for route: {task.route_name}")

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
                    logger.warning(f"No route found for {task.mode} "
                                 f"{'(routed)' if task.is_routed else '(direct)'}")
                return None

            # Process only the first route and clear result to free memory
            route_metrics = self.calculate_route_metrics(result[0])
            if self.debug:
                logger.info(f"Calculated metrics for {task.mode}: {route_metrics}")
            del result
            return route_metrics

        except Exception as e:
            logger.error(f"Error processing task: {str(e)}")
            return {'error': str(e)}
        finally:
            gc.collect()  # Force garbage collection after each task

    def calculate_route_metrics(self, route: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate metrics for a route."""
        legs = route.get('legs', [])
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
        """Extract leg details from route legs."""
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

    def process_route(self, route_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single route with all its modes using the thread pool."""
        try:
            route_name = route_data.get('route_name', 'Unnamed Route')
            if self.debug:
                logger.info(f"Processing route: {route_name}")

            route_metrics = {
                'route_name': route_name,
                'route_description': route_data.get('route_description', 'No description available'),
                'timestamp': datetime.now().isoformat(),
                'modes': {},
                'status': 'success'
            }

            # Create and process tasks
            tasks = self.create_route_tasks(route_data)
            if not tasks:
                route_metrics['status'] = 'error'
                route_metrics['error'] = 'No valid tasks created for route'
                return route_metrics

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
                        route_metrics['modes'][mode_key] = result
                        if self.debug:
                            logger.info(f"Added {mode_key} metrics to route")
                except Exception as e:
                    logger.error(f"Error processing {task.mode} route: {str(e)}")
                finally:
                    # Clear the future to free memory
                    future.cancel()

            if self.debug:
                logger.info(f"Final route_metrics: {route_metrics}")
            return route_metrics

        except Exception as e:
            logger.error(f"Error processing route: {str(e)}")
            return {
                'route_name': route_name,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
        finally:
            gc.collect()  # Force garbage collection after processing route