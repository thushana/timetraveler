import pytest
from unittest.mock import Mock, patch
import json
from datetime import datetime

# Sample test data
SAMPLE_MAPS_URL = "https://www.google.com/maps/place/Shoreline+Park/@37.7622754,-122.279488,14z/data=!4m44!1m37!4m36!1m6!1m2!1s0x808f80d8f2cf1595:0xdf3815440c2316a8!2sPPQR%2B8V,+Alameda,+CA!2m2!1d-122.2578125!2d37.7383125"

SAMPLE_PLUS_CODES = [
    {'plus_code': 'PPQR+8V', 'location': 'Alameda,+CA'},
    {'plus_code': 'QQ52+4G', 'location': 'Alameda,+CA'}
]

SAMPLE_PLACE_RESULT = {
    'candidates': [{
        'geometry': {
            'location': {
                'lat': 37.7383125,
                'lng': -122.2578125
            }
        }
    }]
}

SAMPLE_REVERSE_GEOCODE = [{
    'place_id': 'ChIJm7F2UQSEj4ARSeNPlO18Yss',
    'formatted_address': '152 Sweet Rd, Alameda, CA 94502, USA',
}]

SAMPLE_ROUTES_JSON = {
    "routes": [
        {
            "route_name": "Target Run",
            "route_url": SAMPLE_MAPS_URL,
            "route_description": "Test route description"
        }
    ]
}

SAMPLE_ENRICHED_WAYPOINT = {
    'plus_code': 'PPQR+8V',
    'place_id': 'ChIJm7F2UQSEj4ARSeNPlO18Yss',
    'formatted_address': '152 Sweet Rd, Alameda, CA 94502, USA',
    'latitude': 37.7383125,
    'longitude': -122.2578125
}

@pytest.fixture
def mock_gmaps():
    """Create a mock Google Maps client"""
    mock = Mock()
    mock.find_place.return_value = SAMPLE_PLACE_RESULT
    mock.reverse_geocode.return_value = SAMPLE_REVERSE_GEOCODE
    return mock

@pytest.fixture
def processor(mock_gmaps):
    """Create a RoutePreProcessor instance with mock gmaps"""
    from route_preprocessor import RoutePreProcessor
    with patch('googlemaps.Client', return_value=mock_gmaps):
        processor = RoutePreProcessor('fake-api-key')
    return processor

@pytest.fixture
def sample_routes_file(tmp_path):
    """Create a temporary routes.json file"""
    routes_file = tmp_path / "routes.json"
    routes_file.write_text(json.dumps(SAMPLE_ROUTES_JSON))
    return routes_file

@pytest.fixture
def nonexistent_dir_file(tmp_path):
    """Create a path to a file in a nonexistent directory"""
    nonexistent_dir = tmp_path / "nonexistent"
    return nonexistent_dir / "output.json"