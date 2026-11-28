import unittest
from unittest.mock import Mock, patch

import requests
from weather_agent import WeatherAgent


class WeatherAgentTests(unittest.TestCase):
    def test_nearest_hourly_probability(self):
        response = Mock()
        response.json.return_value = {
            "current": {"time": "2026-11-28T08:30", "temperature_2m": 22},
            "current_units": {"temperature_2m": "°C"},
            "hourly": {
                "time": ["2026-11-28T08:00", "2026-11-28T09:00"],
                "precipitation_probability": [10, 70],
            },
        }
        response.raise_for_status.return_value = None
        with patch("weather_agent.requests.get", return_value=response) as get:
            result = WeatherAgent().get_weather(12.9, 77.6)
        self.assertEqual(result["precipitation_probability"], 10)
        self.assertEqual(result["temperature"], 22)
        self.assertEqual(get.call_args.kwargs["timeout"], 10)
        self.assertEqual(get.call_args.kwargs["params"]["hourly"], "precipitation_probability")

    def test_missing_hourly_probability_is_not_reported_as_zero(self):
        response = Mock()
        response.json.return_value = {
            "current": {"time": "2026-11-28T08:00", "temperature_2m": 22},
            "current_units": {"temperature_2m": "°C"},
        }
        response.raise_for_status.return_value = None
        with patch("weather_agent.requests.get", return_value=response):
            result = WeatherAgent().get_weather(12.9, 77.6)
        self.assertIsNone(result["precipitation_probability"])
        self.assertEqual(
            WeatherAgent().format_weather_response("Bengaluru", result),
            "In Bengaluru it's currently 22°C.",
        )

    def test_request_error_returns_none(self):
        with patch("weather_agent.requests.get", side_effect=requests.exceptions.Timeout):
            self.assertIsNone(WeatherAgent().get_weather(12.9, 77.6))


if __name__ == "__main__":
    unittest.main()
