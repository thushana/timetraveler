import pytest
from unittest.mock import Mock, patch, mock_open
import json
import sys
import importlib
from route_preprocessor import RoutePreProcessor, main
from conftest import (
    SAMPLE_MAPS_URL, SAMPLE_PLUS_CODES, SAMPLE_REVERSE_GEOCODE,
    SAMPLE_PLACE_RESULT, SAMPLE_ROUTES_JSON, SAMPLE_ENRICHED_WAYPOINT
)

class TestRoutePreProcessor:
    def test_extract_plus_codes(self, processor):
        """Test extraction of plus codes from URL"""
        result = processor.extract_plus_codes(SAMPLE_MAPS_URL)
        assert len(result) == 1
        assert result[0]['plus_code'] == 'PPQR+8V'
        assert result[0]['location'] == 'Alameda,+CA'  # URL encoded format

    def test_extract_plus_codes_invalid_url(self, processor):
        """Test handling of URL without plus codes"""
        with pytest.raises(ValueError, match="No Plus Codes found in the URL"):
            processor.extract_plus_codes("https://www.google.com/maps")

    def test_enrich_waypoint_data(self, processor, mock_gmaps):
        """Test enrichment of waypoint data"""
        waypoint = SAMPLE_PLUS_CODES[0]
        result = processor.enrich_waypoint_data(waypoint)
        
        assert result['plus_code'] == waypoint['plus_code']
        assert result['place_id'] == SAMPLE_REVERSE_GEOCODE[0]['place_id']
        assert result['formatted_address'] == SAMPLE_REVERSE_GEOCODE[0]['formatted_address']
        assert result['latitude'] == SAMPLE_PLACE_RESULT['candidates'][0]['geometry']['location']['lat']
        assert result['longitude'] == SAMPLE_PLACE_RESULT['candidates'][0]['geometry']['location']['lng']

    def test_enrich_waypoint_data_no_results(self, processor, mock_gmaps):
        """Test handling of waypoint with no results"""
        mock_gmaps.find_place.return_value = {'candidates': []}
        
        with pytest.raises(ValueError, match="Could not find coordinates"):
            processor.enrich_waypoint_data(SAMPLE_PLUS_CODES[0])

    def test_process_route(self, processor):
        """Test processing of a complete route"""
        result = processor.process_route(SAMPLE_MAPS_URL, "Test Route")
        
        assert result['route_name'] == "Test Route"
        assert 'created_at' in result
        assert len(result['waypoints']) == 1
        assert result['original_url'] == SAMPLE_MAPS_URL

    def test_process_routes_file(self, processor, sample_routes_file, tmp_path):
        """Test processing of routes file"""
        output_file = tmp_path / "routes_enriched.json"
        with patch('builtins.open', mock_open(read_data=json.dumps(SAMPLE_ROUTES_JSON))):
            result = processor.process_routes_file(
                routes_filename=str(sample_routes_file),
                output_filename=str(output_file)
            )
            
        assert len(result['routes']) == 1
        assert result['routes'][0]['route_name'] == "Target Run"
        assert len(result['routes'][0]['waypoints']) == 1

    def test_process_routes_file_not_found(self, processor):
        """Test handling of missing routes file"""
        with pytest.raises(FileNotFoundError):
            processor.process_routes_file("nonexistent.json")

    def test_process_routes_file_invalid_json(self, processor):
        """Test handling of invalid JSON in routes file"""
        with patch('builtins.open', mock_open(read_data="invalid json")):
            with pytest.raises(ValueError, match="Invalid JSON"):
                processor.process_routes_file()

    def test_print_routes_summary(self, processor, capsys):
        """Test routes summary printing"""
        test_data = {
            'routes': [
                {
                    'route_name': 'Test Route',
                    'route_description': 'Test Description',
                    'created_at': '2025-01-01T00:00:00',
                    'waypoints': [SAMPLE_ENRICHED_WAYPOINT]
                }
            ]
        }
        
        processor.print_routes_summary(test_data)
        captured = capsys.readouterr()
        
        assert "Test Route" in captured.out
        assert "Test Description" in captured.out
        assert "Number of waypoints: 1" in captured.out

    def test_print_json(self, processor, capsys):
        """Test JSON printing"""
        test_data = {'test': 'data'}
        processor.print_json(test_data)
        captured = capsys.readouterr()
        
        assert json.loads(captured.out.split("JSON Output:")[-1].strip()) == test_data

    def test_reverse_geocode_no_results(self, processor, mock_gmaps):
        """Test handling of no reverse geocode results"""
        mock_gmaps.find_place.return_value = SAMPLE_PLACE_RESULT
        mock_gmaps.reverse_geocode.return_value = []
        
        with pytest.raises(ValueError, match="Could not find place details"):
            processor.enrich_waypoint_data(SAMPLE_PLUS_CODES[0])

    def test_process_route_error_handling(self, processor, mock_gmaps):
        """Test error handling in process_route"""
        mock_gmaps.find_place.side_effect = Exception("Test error")
        result = processor.process_route(SAMPLE_MAPS_URL, "Test Route")
        assert result['waypoints'] == []

    def test_process_routes_file_output_error(self, processor, sample_routes_file, tmp_path):
        """Test handling of output file write error"""
        output_file = tmp_path / "nonexistent" / "routes_enriched.json"
        with pytest.raises(IOError):
            processor.process_routes_file(
                routes_filename=str(sample_routes_file),
                output_filename=str(output_file)
            )

    def test_enrich_waypoint_data_no_reverse_geocode(self, processor, mock_gmaps):
        """Test handling of waypoint with no reverse geocode results"""
        mock_gmaps.reverse_geocode.return_value = []
        
        with pytest.raises(ValueError, match="Could not find place details"):
            processor.enrich_waypoint_data(SAMPLE_PLUS_CODES[0])


class TestMain:
    def test_main_missing_api_key(self):
        """Test main function with missing API key"""
        with patch.object(sys, 'argv', ['script.py', '--json']), \
             patch('os.getenv', return_value=None), \
             pytest.raises(ValueError, match="GOOGLE_MAPS_API_KEY environment variable is not set"):
            main()

    def test_main_with_json_flag(self):
        """Test main function with --json flag"""
        with patch.object(sys, 'argv', ['script.py', '--json']), \
             patch('os.getenv', return_value='fake-api-key'), \
             patch('route_preprocessor.RoutePreProcessor') as MockProcessor:
            mock_processor = Mock()
            MockProcessor.return_value = mock_processor
            mock_processor.process_routes_file.return_value = {'test': 'data'}
            
            main()
            mock_processor.print_json.assert_called_once_with({'test': 'data'})

    def test_main_without_json_flag(self):
        """Test main function with default summary output"""
        with patch.object(sys, 'argv', ['script.py', '--summary']), \
             patch('os.getenv', return_value='fake-api-key'), \
             patch('route_preprocessor.RoutePreProcessor') as MockProcessor:
            mock_processor = Mock()
            MockProcessor.return_value = mock_processor
            mock_processor.process_routes_file.return_value = {'test': 'data'}
            
            main()
            mock_processor.print_routes_summary.assert_called_once_with({'test': 'data'})

    def test_main_no_args(self):
        """Test main function with no arguments"""
        with patch.object(sys, 'argv', ['script.py']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1