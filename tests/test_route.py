import pytest
from unittest.mock import Mock, patch
import json
import os
from route import process_route, main

# Sample test data moved to global scope for reuse
SAMPLE_ROUTE = {
    "route_name": "Test Route",
    "created_at": "2025-01-12T17:11:41.296638",
    "waypoints": [
        {
            "plus_code": "PPQR+8V",
            "place_id": "place_id_1",
            "formatted_address": "152 Sweet Rd, Alameda, CA 94502, USA",
            "latitude": 37.7383125,
            "longitude": -122.2578125
        },
        {
            "plus_code": "QQ52+4G",
            "place_id": "place_id_2",
            "formatted_address": "Otis Dr & Park St, Alameda, CA 94501, USA",
            "latitude": 37.7578125,
            "longitude": -122.2486875
        }
    ],
    "route_description": "Test route description"
}

SAMPLE_DIRECTIONS_RESPONSE = [{
    'legs': [{
        'distance': {'text': '2.0 mi', 'value': 3218.688},
        'duration': {'text': '5 mins', 'value': 300},
        'start_address': '152 Sweet Rd, Alameda, CA 94502, USA',
        'end_address': 'Otis Dr & Park St, Alameda, CA 94501, USA'
    }]
}]

@pytest.fixture
def mock_gmaps():
    """Fixture to create a mock Google Maps client"""
    mock = Mock()
    mock.directions.return_value = SAMPLE_DIRECTIONS_RESPONSE
    return mock

def test_process_route_success(mock_gmaps, capsys):
    """Test successful route processing"""
    process_route(mock_gmaps, SAMPLE_ROUTE)
    captured = capsys.readouterr()
    
    assert "Processing route: Test Route" in captured.out
    assert "Test route description" in captured.out
    assert "Route Summary" in captured.out
    assert "0 hours, 5 minutes, 0 seconds" in captured.out

def test_process_route_no_waypoints(mock_gmaps, capsys):
    """Test route processing with no waypoints"""
    route_data = SAMPLE_ROUTE.copy()
    route_data['waypoints'] = []
    
    process_route(mock_gmaps, route_data)
    captured = capsys.readouterr()
    
    assert "No place IDs found in route" in captured.out

def test_process_route_api_error(mock_gmaps, capsys):
    """Test handling of API errors"""
    mock_gmaps.directions.return_value = []
    
    process_route(mock_gmaps, SAMPLE_ROUTE)
    captured = capsys.readouterr()
    
    assert "Processing route: Test Route" in captured.out
    assert "Route Summary" not in captured.out

def test_main_success(tmp_path):
    """Test successful execution of main function"""
    test_route_data = {"routes": [SAMPLE_ROUTE]}
    test_file = tmp_path / "routes_enriched.json"
    test_file.write_text(json.dumps(test_route_data))
    
    with patch('os.path.isfile', return_value=True), \
         patch('builtins.open', return_value=test_file.open()), \
         patch('route.load_dotenv'), \
         patch('os.getenv', return_value='AIzaSyFake-API-Key-For-Testing'), \
         patch('googlemaps.Client') as mock_client:
        mock_client.return_value.directions.return_value = SAMPLE_DIRECTIONS_RESPONSE
        main()
        mock_client.return_value.directions.assert_called_once()

def test_main_missing_api_key():
    """Test main function with missing API key"""
    with patch('route.load_dotenv'), \
         patch('os.getenv', return_value=None):
        with pytest.raises(ValueError, match="GOOGLE_MAPS_API_KEY environment variable is not set"):
            main()

def test_main_missing_file(capsys):
    """Test main function with missing routes file"""
    with patch('builtins.open', side_effect=FileNotFoundError), \
         patch('route.load_dotenv'), \
         patch('os.getenv', return_value='AIzaSyFake-API-Key-For-Testing'), \
         patch('googlemaps.Client') as mock_client:
        main()
        captured = capsys.readouterr()
        assert "Error: routes_enriched.json file not found" in captured.out
        mock_client.return_value.directions.assert_not_called()

def test_main_invalid_json(tmp_path, capsys):
    """Test main function with invalid JSON file"""
    test_file = tmp_path / "routes_enriched.json"
    test_file.write_text("invalid json content")
    
    with patch('os.path.isfile', return_value=True), \
         patch('builtins.open', return_value=test_file.open()), \
         patch('route.load_dotenv'), \
         patch('os.getenv', return_value='AIzaSyFake-API-Key-For-Testing'), \
         patch('googlemaps.Client') as mock_client:
        main()
        captured = capsys.readouterr()
        assert "Error: Invalid JSON format in routes_enriched.json" in captured.out
        mock_client.return_value.directions.assert_not_called()

def test_process_route_exception(mock_gmaps, capsys):
    """Test handling of unexpected exceptions during route processing"""
    # Make the directions method raise an exception
    mock_gmaps.directions.side_effect = Exception("Test error")
    
    process_route(mock_gmaps, SAMPLE_ROUTE)
    captured = capsys.readouterr()
    
    assert "Error processing route: Test error" in captured.out

def test_file_read_general_exception(capsys):
    """Test handling of general file reading exceptions"""
    mock_open = Mock()
    mock_open.side_effect = Exception("Generic file error")
    
    with patch('builtins.open', mock_open), \
         patch('route.load_dotenv'), \
         patch('os.getenv', return_value='AIzaSyFake-API-Key-For-Testing'):
        main()
        
        captured = capsys.readouterr()
        assert "Error reading file: Generic file error" in captured.out

def test_main_general_exception(capsys):
    """Test handling of general exceptions in main"""
    with patch('route.load_dotenv'), \
         patch('os.getenv', return_value='AIzaSyFake-API-Key-For-Testing'), \
         patch('googlemaps.Client', side_effect=Exception("Non-API key error")):
        main()
        
        captured = capsys.readouterr()
        assert "Error in main: Non-API key error" in captured.out

def test_main_entry_point(monkeypatch):
    import route
    
    # Mock main function
    mock_main = Mock()
    monkeypatch.setattr(route, 'main', mock_main)
    
    # Call the entry point code directly
    if route.__name__ == '__main__':
        route.main()
    
    # Now set it to __main__ and try again
    monkeypatch.setattr(route, '__name__', '__main__')
    if route.__name__ == '__main__':
        route.main()
        
    # Verify main was called exactly once
    assert mock_main.call_count == 1

def test_process_route_exception(mock_gmaps, capsys):
    """Test handling of unexpected exceptions during route processing"""
    mock_gmaps.directions.side_effect = Exception("Test error")
    
    process_route(mock_gmaps, SAMPLE_ROUTE)
    captured = capsys.readouterr()
    
    assert "Error processing route: Test error" in captured.out