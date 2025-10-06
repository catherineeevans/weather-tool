import unittest
from unittest.mock import patch, Mock
from app import app, get_request_params, get_cached_weather, pull_weather_response, parse_weather_data, cache
from datetime import datetime, timedelta
import requests

class TestApp(unittest.TestCase):

    def test_get_request_params(self):
        with app.test_request_context("/weather?zip_code=20001&units=metric"):
            zip_code, units, country = get_request_params()
            self.assertEqual(zip_code, "20001")
            self.assertEqual(units, "metric")
            self.assertEqual(country, "us")

    def test_get_cached_weather_valid(self):
        cache_key = "20001_imperial"
        cache[cache_key] = ({"temp": 70}, datetime.now() + timedelta(minutes=5))
        result = get_cached_weather(cache_key)
        self.assertEqual(result, {"temp": 70})

    def test_get_cached_weather_expired(self):
        cache_key = "20001_imperial"
        cache[cache_key] = ({"temp": 70}, datetime.now() - timedelta(minutes=10))
        result = get_cached_weather(cache_key)
        self.assertIsNone(result)
        self.assertNotIn(cache_key, cache)

    @patch("app.requests.get")
    def test_pull_weather_response_success(self, mock_get):
        mock_response = Mock()
        mock_get.return_value = mock_response
        result = pull_weather_response("20001", "us", "imperial")
        mock_get.assert_called_once()
        self.assertEqual(result, mock_response)

    @patch("app.requests.get", side_effect=requests.Timeout)
    def test_pull_weather_response_timeout(self, mock_get):
        result = pull_weather_response("20001", "us", "imperial")
        self.assertIsNone(result)

    def test_parse_weather_data_valid(self):
        data = {
            "name": "Seattle",
            "sys": {"country": "US"},
            "main": {"temp": 70, "temp_min": 60, "temp_max": 75},
            "weather": [{"description": "clear sky"}]
        }
        result = parse_weather_data(data)
        self.assertEqual(result["city"], "Seattle")
        self.assertIn("description", result)

    def test_parse_weather_data_invalid(self):
        with self.assertRaises(Exception):
            parse_weather_data({"bad": "data"})

if __name__ == "__main__":
    unittest.main()
