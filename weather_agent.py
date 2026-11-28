"""
Weather Agent - Fetches weather information using Open-Meteo API.
"""
from datetime import datetime
from typing import Optional, Dict

import requests


class WeatherAgent:
    """Child agent responsible for fetching weather data."""

    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1/forecast"

    @staticmethod
    def _nearest_hourly_probability(current_time, hourly_times, probabilities):
        """Select the hourly precipitation probability closest to current time."""
        if (
            not isinstance(current_time, str)
            or not isinstance(hourly_times, list)
            or not isinstance(probabilities, list)
            or not hourly_times
            or not probabilities
        ):
            return None

        try:
            current = datetime.fromisoformat(current_time.replace("Z", "+00:00"))
            valid = []
            for index, value in enumerate(hourly_times):
                if index >= len(probabilities) or probabilities[index] is None:
                    continue
                if not isinstance(value, str):
                    continue
                try:
                    forecast_time = datetime.fromisoformat(value.replace("Z", "+00:00"))
                    if current.tzinfo and forecast_time.tzinfo:
                        distance = abs((current - forecast_time).total_seconds())
                    else:
                        distance = abs(
                            (current.replace(tzinfo=None) - forecast_time.replace(tzinfo=None)).total_seconds()
                        )
                    valid.append((distance, probabilities[index]))
                except (TypeError, ValueError):
                    continue
            return min(valid, key=lambda item: item[0])[1] if valid else None
        except (TypeError, ValueError):
            return None

    def get_weather(self, latitude: float, longitude: float) -> Optional[Dict]:
        """Get current temperature and the nearest hourly rain probability."""
        try:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m",
                "hourly": "precipitation_probability",
                "forecast_days": 1,
            }
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            current = data.get("current")
            if not isinstance(current, dict) or current.get("temperature_2m") is None:
                return None

            hourly = data.get("hourly") or {}
            rain_chance = self._nearest_hourly_probability(
                current.get("time"),
                hourly.get("time", []),
                hourly.get("precipitation_probability", []),
            )
            units = data.get("current_units") or {}
            return {
                "temperature": current.get("temperature_2m"),
                "precipitation_probability": rain_chance,
                "unit": units.get("temperature_2m", "°C"),
            }
        except requests.exceptions.RequestException as e:
            print(f"Weather API error: {e}")
            return None
        except (TypeError, ValueError, KeyError, AttributeError) as e:
            print(f"Error parsing weather response: {e}")
            return None

    def format_weather_response(self, place_name: str, weather_data: Dict) -> str:
        if not weather_data:
            return f"Sorry, I couldn't fetch weather information for {place_name}."
        temp = weather_data.get("temperature")
        unit = weather_data.get("unit", "°C")
        rain_chance = weather_data.get("precipitation_probability")
        if rain_chance is None:
            return f"In {place_name} it's currently {temp}{unit}."
        return f"In {place_name} it's currently {temp}{unit} with a {rain_chance}% chance of rain."
