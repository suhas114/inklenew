"""
Parent Tourism AI Agent - Orchestrates Weather and Places agents

This parent agent coordinates the child agents:
- Weather Agent: Uses Open-Meteo API (external API source)
- Places Agent: Uses Nominatim + Overpass APIs (external API sources)

The parent agent uses pattern matching (not AI) to extract place names
and verifies them using the Nominatim API. All data comes from
external APIs, not from AI knowledge.
"""
from weather_agent import WeatherAgent
from places_agent import PlacesAgent
import os
import re
from typing import Optional
from dotenv import load_dotenv

# Load .env file, ignore if it doesn't exist or has encoding issues
try:
    load_dotenv(encoding='utf-8')
except Exception:
    # If .env file has issues, try loading without explicit encoding
    try:
        load_dotenv()
    except Exception:
        pass  # Continue without .env file, user can set env var directly


class TourismAgent:
    """Parent Agent that orchestrates the tourism system"""
    
    def __init__(self):
        self.weather_agent = WeatherAgent()
        self.places_agent = PlacesAgent()
    
    def extract_place_name(self, user_input: str) -> Optional[str]:
        """
        Extract place name from user input using pattern matching
        
        Args:
            user_input: User's input text
            
        Returns:
            Extracted place name or None
        """
        # Common patterns for place names in queries
        # Try patterns that match common query structures
        patterns = [
            r"going to go to ([A-Z][a-zA-Z\s]+?)(?:,|\.|$|\?|let|what|and|'s)",
            r"going to ([A-Z][a-zA-Z\s]+?)(?:,|\.|$|\?|let|what|and|'s)",
            r"visit ([A-Z][a-zA-Z\s]+?)(?:,|\.|$|\?|let|what|and)",
            r"in ([A-Z][a-zA-Z\s]+?)(?:,|\.|$|\?|let|what|and|it|the|'s)",
            r"to ([A-Z][a-zA-Z\s]+?)(?:,|\.|$|\?|let|what|and|'s)",
        ]
        
        # Try each pattern
        for pattern in patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                place_name = match.group(1).strip()
                # Clean up common trailing words and punctuation
                place_name = re.sub(r"\s+(let|what|and|the|is|there|are|can|go|visit|going|plan|trip|'s).*$", '', place_name, flags=re.IGNORECASE)
                place_name = place_name.strip(' ,.\'')
                
                # Skip if it's too short or looks like a common word
                if len(place_name) > 2 and place_name.lower() not in ['i', 'me', 'my', 'we', 'us', 'the', 'a', 'an']:
                    # Verify it's a valid place by checking if we can get coordinates
                    coords = self.places_agent.get_coordinates(place_name)
                    if coords:
                        return place_name
        
        # Fallback: try to find capitalized words that might be place names
        words = user_input.split()
        capitalized_phrases = []
        current_phrase = []
        
        for word in words:
            # Remove punctuation
            clean_word = re.sub(r'[^\w\s]', '', word)
            if clean_word and clean_word[0].isupper() and len(clean_word) > 2:
                current_phrase.append(clean_word)
            else:
                if current_phrase:
                    phrase = ' '.join(current_phrase)
                    if len(phrase) > 2:
                        capitalized_phrases.append(phrase)
                    current_phrase = []
        
        # Check the last phrase if we ended with capitalized words
        if current_phrase:
            phrase = ' '.join(current_phrase)
            if len(phrase) > 2:
                capitalized_phrases.append(phrase)
        
        # Try each capitalized phrase as a potential place name
        for phrase in capitalized_phrases:
            # Skip common non-place words
            if phrase.lower() not in ['i', 'me', 'my', 'we', 'us', 'the', 'a', 'an', 'let', 'what', 'and']:
                if self.places_agent.get_coordinates(phrase):
                    return phrase
        
        return None
    
    def determine_intent(self, user_input: str) -> dict:
        """
        Determine what the user wants: weather, places, or both
        
        Args:
            user_input: User's input text
            
        Returns:
            Dictionary with intent flags
        """
        user_lower = user_input.lower()
        
        # Check for explicit weather-related keywords
        wants_weather = any(keyword in user_lower for keyword in [
            "temperature", "weather", "rain", "forecast", "climate"
        ])
        
        # Check for explicit places-related keywords (excluding "go" in "going to")
        # Only match if it's clearly about places/attractions, not just "going to"
        explicit_places_keywords = any(keyword in user_lower for keyword in [
            "places", "visit", "attractions", "tourist", "see", "plan", "trip"
        ])
        
        # Check for "go" but only if it's in context of visiting/seeing places
        # Not just "going to [place]"
        has_go_context = any(phrase in user_lower for phrase in [
            "places to go", "go to visit", "go see", "where to go"
        ])
        
        wants_places = explicit_places_keywords or has_go_context
        
        # If user asks about weather/temperature, only return weather unless they also ask for places
        if wants_weather and not explicit_places_keywords and not has_go_context:
            # If they only ask about weather, don't include places
            wants_places = False
        
        # If neither is explicitly mentioned, default to places
        if not wants_weather and not wants_places:
            wants_places = True
        
        return {
            "weather": wants_weather,
            "places": wants_places
        }
    
    def verify_place_exists(self, place_name: str) -> bool:
        """
        Verify if a place exists by trying to get its coordinates
        
        Args:
            place_name: Name of the place to verify
            
        Returns:
            True if place exists, False otherwise
        """
        coords = self.places_agent.get_coordinates(place_name)
        return coords is not None
    
    def process_query(self, user_input: str) -> str:
        """
        Process user query and return appropriate response
        
        Args:
            user_input: User's input text
            
        Returns:
            Formatted response string
        """
        # Extract place name
        place_name = self.extract_place_name(user_input)
        
        if not place_name:
            return "I couldn't identify a place name in your query. Please specify a place you want to visit."
        
        # Verify place exists
        if not self.verify_place_exists(place_name):
            return f"I don't know if this place exists."
        
        # Determine intent
        intent = self.determine_intent(user_input)
        
        responses = []
        places_list = None
        
        # Get weather if requested
        if intent["weather"]:
            coords = self.places_agent.get_coordinates(place_name)
            if coords:
                lat, lon = coords
                weather_data = self.weather_agent.get_weather(lat, lon)
                if weather_data:
                    weather_response = self.weather_agent.format_weather_response(place_name, weather_data)
                    responses.append(weather_response)
        
        # Get places if requested
        if intent["places"]:
            places_list = self.places_agent.get_places_for_location(place_name, limit=5)
            if places_list:
                places_response = self.places_agent.format_places_response(place_name, places_list)
                responses.append(places_response)
        
        # Combine responses
        if not responses:
            return f"Sorry, I couldn't fetch information for {place_name}. Please try again."
        
        # Format combined response
        if len(responses) == 2 and places_list:
            # Both weather and places
            # Remove trailing period from weather response if present
            weather_text = responses[0].rstrip('. ')
            return f"{weather_text}. And these are the places you can go:\n\n" + "\n".join(places_list)
        else:
            return responses[0]

