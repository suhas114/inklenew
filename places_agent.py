"""
Places Agent - Fetches tourist attractions using Overpass API

This child agent uses external API sources:
1. Nominatim API - For geocoding (converting place names to coordinates)
2. Overpass API - For finding tourist attractions from OpenStreetMap data

It does NOT use AI knowledge or LLM responses. All place data comes
directly from these open-source APIs.
"""
import math
import requests
from typing import Optional, List


class PlacesAgent:
    """Child Agent responsible for finding tourist attractions"""

    def __init__(self):
        self.overpass_url = "https://overpass-api.de/api/interpreter"
        self.nominatim_url = "https://nominatim.openstreetmap.org/search"
        # Reuse successful geocoding results to avoid redundant Nominatim calls.
        self._coordinate_cache = {}

    def get_coordinates(self, place_name: str) -> Optional[tuple]:
        """
        Get coordinates (lat, lon) for a place using Nominatim API.

        Args:
            place_name: Name of the place

        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        if not isinstance(place_name, str) or not place_name.strip():
            return None

        cache_key = place_name.strip().casefold()
        if cache_key in self._coordinate_cache:
            return self._coordinate_cache[cache_key]

        try:
            params = {
                "q": place_name.strip(),
                "format": "json",
                "limit": 1
            }

            headers = {
                "User-Agent": "Tourism-Agent/1.0 (https://github.com/suhas114/inklenew)"
            }

            response = requests.get(self.nominatim_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data and len(data) > 0:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                if math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180:
                    coordinates = (lat, lon)
                    self._coordinate_cache[cache_key] = coordinates
                    return coordinates

            return None

        except requests.exceptions.RequestException as e:
            print(f"Geocoding API error: {e}")
            return None
        except (KeyError, ValueError, IndexError) as e:
            print(f"Error parsing geocoding response: {e}")
            return None
        except Exception as e:
            print(f"Error getting coordinates: {e}")
            return None

    def get_tourist_attractions(self, latitude: float, longitude: float, limit: int = 5) -> Optional[List[str]]:
        """
        Get tourist attractions near given coordinates using Overpass API.

        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            limit: Maximum number of places to return (default: 5)

        Returns:
            List of place names or None if error
        """
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            return None

        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except (TypeError, ValueError):
            return None

        if (
            not math.isfinite(latitude)
            or not math.isfinite(longitude)
            or not -90 <= latitude <= 90
            or not -180 <= longitude <= 180
        ):
            return None

        try:
            # Overpass QL query to find tourist attractions within 10km radius
            query = f"""
            [out:json][timeout:25];
            (
              node["tourism"~"^(attraction|museum|zoo|theme_park|gallery|monument|artwork|viewpoint)$"](around:10000,{latitude},{longitude});
              way["tourism"~"^(attraction|museum|zoo|theme_park|gallery|monument|artwork|viewpoint)$"](around:10000,{latitude},{longitude});
              node["leisure"~"^(park|nature_reserve|stadium)$"](around:10000,{latitude},{longitude});
              way["leisure"~"^(park|nature_reserve|stadium)$"](around:10000,{latitude},{longitude});
            );
            out body;
            """

            response = requests.post(
                self.overpass_url,
                data=query,
                headers={"Content-Type": "text/plain"},
                timeout=30
            )
            response.raise_for_status()

            data = response.json()

            places = []
            seen_names = set()

            if "elements" in data:
                for element in data["elements"]:
                    if "tags" in element:
                        name = element["tags"].get("name")
                        if name and name not in seen_names:
                            places.append(name)
                            seen_names.add(name)

                            if len(places) >= limit:
                                break

            return places if places else None

        except requests.exceptions.RequestException as e:
            print(f"Overpass API error: {e}")
            return None
        except (KeyError, ValueError) as e:
            print(f"Error parsing Overpass response: {e}")
            return None
        except Exception as e:
            print(f"Error fetching tourist attractions: {e}")
            return None

    def get_places_for_location(self, place_name: str, limit: int = 5) -> Optional[List[str]]:
        """
        Get tourist attractions for a place name (handles geocoding internally).

        Args:
            place_name: Name of the place
            limit: Maximum number of places to return

        Returns:
            List of place names or None if error
        """
        coords = self.get_coordinates(place_name)
        if not coords:
            return None

        lat, lon = coords
        return self.get_tourist_attractions(lat, lon, limit)

    def format_places_response(self, place_name: str, places: List[str]) -> str:
        """
        Format places list into a user-friendly response.

        Args:
            place_name: Name of the place
            places: List of tourist attraction names

        Returns:
            Formatted string response
        """
        if not places:
            return f"Sorry, I couldn't find tourist attractions for {place_name}."

        response = f"In {place_name} these are the places you can go,\n\n"
        for place in places:
            response += f"{place}\n"

        return response.strip()
