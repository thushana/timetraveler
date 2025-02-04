# Standard Library
from typing import Dict, Any, List
import logging

# Application
from core.config import settings

logger = logging.getLogger(__name__)

class JourneyReporter:
    def __init__(self, debug: bool = None):
        """Initialize reporter with optional debug override.
        
        Args:
            debug: Optional override for debug mode (default from settings)
        """
        self.debug = debug if debug is not None else settings.DEBUG

    @staticmethod
    def format_duration(seconds: int) -> str:
        """Format duration in seconds to hours, minutes, seconds string."""
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"

    @staticmethod
    def meters_to_miles(meters: float) -> float:
        """Convert meters to miles."""
        return meters / 1609.34

    @staticmethod
    def kph_to_mph(kph: float) -> float:
        """Convert kilometers per hour to miles per hour."""
        return kph * 0.621371

    @staticmethod
    def get_mode_emoji(mode: str) -> str:
        """Get the appropriate emoji for a travel mode."""
        emoji_map = {
            'driving': '🚗',
            'driving_routed': '🚙',
            'bicycling': '🚲',
            'walking': '🚶',
            'transit': '🚌'
        }
        return emoji_map.get(mode, '🗺️')  # Default to map emoji if mode not found

    def print_mode_details(self, mode: str, mode_data: Dict[str, Any], indent: str = "") -> None:
        """Print details for a specific travel mode."""
        if not mode_data or 'metrics' not in mode_data:
            if self.debug:
                logger.warning(f"No metrics data found for mode: {mode}")
            return

        metrics = mode_data['metrics']
        emoji = self.get_mode_emoji(mode)
        
        # Print main metrics
        print(f"\n{indent}{emoji} {mode.upper()}:")
        print(f"{indent}Duration: {self.format_duration(metrics['duration_seconds'])}")
        print(f"{indent}Distance: {metrics['distance_meters']/1000:.1f} km ({self.meters_to_miles(metrics['distance_meters']):.1f} miles)")
        if 'speed_kph' in metrics:
            print(f"{indent}Average Speed: {metrics['speed_kph']:.1f} kph ({self.kph_to_mph(metrics['speed_kph']):.1f} mph)")

        # Print leg details if available and more than one leg exists
        if 'leg_details' in mode_data and len(mode_data['leg_details']) > 1:
            if self.debug:
                logger.info(f"Printing {len(mode_data['leg_details'])} legs for {mode}")
                
            print(f"\n{indent}Detailed Leg Information:")
            for i, leg in enumerate(mode_data['leg_details'], 1):
                print(f"\n{indent}🔸 Leg {i}:")
                print(f"{indent}From: {leg['start_address']}")
                print(f"{indent}To: {leg['end_address']}")
                print(f"{indent}Duration: {self.format_duration(leg['duration_seconds'])}")
                print(f"{indent}Distance: {leg['distance_meters']/1000:.1f} km ({self.meters_to_miles(leg['distance_meters']):.1f} miles)")
                if 'speed_kph' in leg:
                    print(f"{indent}Speed: {leg['speed_kph']:.1f} kph ({self.kph_to_mph(leg['speed_kph']):.1f} mph)")

    def print_route_summary(self, journey_metrics: Dict[str, Any]) -> None:
        """Print a detailed summary of journey metrics including imperial conversions."""
        if self.debug:
            logger.info(f"Printing summary for journey: {journey_metrics['journey_name']}")

        print("\n" + "="* 80)
        print(f"Journey: {journey_metrics['journey_name']}")
        print(f"Description: {journey_metrics['journey_description']}")
        print("=" * 80)

        if self.debug:
            logger.info("Available keys in journey_metrics: %s", journey_metrics.keys())

        # Print all modes except driving_routed first
        print("\n📍 DIRECT ROUTES:")
        print("-" * 40)
        
        for mode, data in journey_metrics['modes'].items():
            if mode != 'driving_routed':  # Skip driving_routed for now
                self.print_mode_details(mode, data, indent="")

        # Print driving_routed separately with more detailed information
        if 'driving_routed' in journey_metrics['modes']:
            print("\n" + "=" * 80)
            print("🛣️ DRIVING (ROUTED WITH WAYPOINTS):")
            print("-" * 40)
            self.print_mode_details('driving_routed', journey_metrics['modes']['driving_routed'], indent="")

        print("\n" + "=" * 80)

    def print_batch_summary(self, completed_routes: List[Dict[str, Any]]) -> None:
        """Print summaries for a batch of completed journeys."""
        if not completed_routes:
            logger.warning("No journeys to summarize")
            return
            
        if self.debug:
            logger.info(f"Printing summaries for {len(completed_routes)} journeys")
            
        for journey_metrics in completed_routes:
            self.print_route_summary(journey_metrics)