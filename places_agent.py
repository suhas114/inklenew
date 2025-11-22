"""
Places Agent - Fetches tourist attractions using Overpass API

This child agent uses external API sources:
1. Nominatim API - For geocoding (converting place names to coordinates)
2. Overpass API - For finding tourist attractions from OpenStreetMap data

It does NOT use AI knowledge or LLM responses. All place data comes
directly from these open-source APIs.
"""
import requests
from typing import Optional, List


class PlacesAgent:
    """Child Agent responsible for finding tourist attractions"""
    
    def __init__(self):
        self.overpass_url = "https://overpass-api.de/api/interpreter"
        self.nominatim_url = "https://nominatim.openstreetmap.org/search"
    
    def get_coordinates(self, place_name: str) -> Optional[tuple]:
        """
        Get coordinates (lat, lon) for a place using Nominatim API
        
        Args:
            place_name: Name of the place
            
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        try:
            params = {
                "q": place_name,
                "format": "json",
                "limit": 1
            }
            
            headers = {
                "User-Agent": "Tourism-Agent/1.0"
            }
            
            response = requests.get(self.nominatim_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data and len(data) > 0:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                return (lat, lon)
            
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
        Get tourist attractions near given coordinates using Overpass API
        
        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            limit: Maximum number of places to return (default: 5)
            
        Returns:
            List of place names or None if error
        """
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
        Get tourist attractions for a place name (handles geocoding internally)
        
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
        Format places list into a user-friendly response
        
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

