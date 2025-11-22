# Multi-Agent Tourism System

A multi-agent system for tourism planning that provides weather information and tourist attraction suggestions for any place.

## Features

- **Parent Agent**: Tourism AI Agent that orchestrates the system
- **Weather Agent**: Fetches current weather and forecast using Open-Meteo API
- **Places Agent**: Suggests up to 5 tourist attractions using Overpass API
- **Error Handling**: Gracefully handles non-existent places

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

**Note**: No API keys required! All child agents use free, open-source APIs:
- Open-Meteo API (weather) - No API key needed
- Nominatim API (geocoding) - No API key needed
- Overpass API (tourist attractions) - No API key needed

## Usage

Run the main application:
```bash
python main.py
```

Then enter your query, for example:
- "I'm going to go to Bangalore, let's plan my trip."
- "I'm going to go to Bangalore, what is the temperature there"
- "I'm going to go to Bangalore, what is the temperature there? And what are the places I can visit?"

## APIs Used (All Open-Source, No API Keys Required)

All child agents use external APIs instead of AI knowledge:

- **Weather Agent** → **Open-Meteo API**: Fetches real-time weather data
  - Endpoint: `https://api.open-meteo.com/v1/forecast`
  - Documentation: https://open-meteo.com/en/docs

- **Places Agent** → **Nominatim API**: Geocoding (converts place names to coordinates)
  - Base URL: `https://nominatim.openstreetmap.org/search`
  - Documentation: https://nominatim.org/release-docs/develop/api/Search/

- **Places Agent** → **Overpass API**: Finds tourist attractions from OpenStreetMap data
  - Base URL: `https://overpass-api.de/api/interpreter`
  - Documentation: https://wiki.openstreetmap.org/wiki/Overpass_API

