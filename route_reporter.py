# Standard Library
from typing import Dict, Any

class RouteReporter:
    def __init__(self, debug: bool = False):
        self.debug = debug

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
            return

        metrics = mode_data['metrics']
        emoji = self.get_mode_emoji(mode)
        print(f"\n{indent}{emoji} {mode.upper()}:")
        print(f"{indent}Duration: {self.format_duration(metrics['duration_seconds'])}")
        print(f"{indent}Distance: {metrics['distance_meters']/1000:.1f} km ({self.meters_to_miles(metrics['distance_meters']):.1f} miles)")
        if 'speed_kph' in metrics:
            print(f"{indent}Average Speed: {metrics['speed_kph']:.1f} kph ({self.kph_to_mph(metrics['speed_kph']):.1f} mph)")

        # Print leg details if available
        if 'leg_details' in mode_data and len(mode_data['leg_details']) > 1:  # Only show if there's more than one leg
            print(f"\n{indent}Detailed Leg Information:")
            for i, leg in enumerate(mode_data['leg_details'], 1):
                print(f"\n{indent}🔸 Leg {i}:")
                print(f"{indent}From: {leg['start_address']}")
                print(f"{indent}To: {leg['end_address']}")
                print(f"{indent}Duration: {self.format_duration(leg['duration_seconds'])}")
                print(f"{indent}Distance: {leg['distance_meters']/1000:.1f} km ({self.meters_to_miles(leg['distance_meters']):.1f} miles)")
                if 'speed_kph' in leg:
                    print(f"{indent}Speed: {leg['speed_kph']:.1f} kph ({self.kph_to_mph(leg['speed_kph']):.1f} mph)")

    def print_route_summary(self, route_metrics: Dict[str, Any]) -> None:
        """Print a detailed summary of route metrics including imperial conversions."""
        print("\n" + "="* 80)
        print(f"Route: {route_metrics['route_name']}")
        print(f"Description: {route_metrics['route_description']}")
        print("=" * 80)

        if self.debug:
            print("\nDebug: Available keys in route_metrics:", route_metrics.keys())

        # Print all modes except driving_routed first
        print("\n📍 DIRECT ROUTES:")
        print("-" * 40)
        
        for mode, data in route_metrics['modes'].items():
            if mode != 'driving_routed':  # Skip driving_routed for now
                self.print_mode_details(mode, data, indent="")

        # Print driving_routed separately with more detailed information
        if 'driving_routed' in route_metrics['modes']:
            print("\n" + "=" * 80)
            print("🛣️ DRIVING (ROUTED WITH WAYPOINTS):")
            print("-" * 40)
            self.print_mode_details('driving_routed', route_metrics['modes']['driving_routed'], indent="")

        print("\n" + "=" * 80)

    def print_batch_summary(self, completed_routes: list) -> None:
        """Print summaries for a batch of completed routes."""
        if self.debug:
            print("\nComplete Route Summaries:")
            for route_metrics in completed_routes:
                self.print_route_summary(route_metrics)