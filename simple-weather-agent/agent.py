from datetime import datetime
import zoneinfo
import httpx
from google.adk.agents import Agent

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def _geocode(city: str) -> dict | None:
    res = httpx.get(GEOCODE_URL, params={"name": city, "count": 1}).json()
    return res["results"][0] if res.get("results") else None


def get_weather(city: str) -> str:
    """Get current weather for a city."""
    loc = _geocode(city)
    if not loc:
        return f"Could not find city: {city}"

    weather = httpx.get(WEATHER_URL, params={
        "latitude": loc["latitude"],
        "longitude": loc["longitude"],
        "current": "temperature_2m,weather_code",
        "temperature_unit": "celsius",
    }).json().get("current", {})

    return f"{city}: {weather.get('temperature_2m')}°C, code {weather.get('weather_code')}"


def get_current_time(city: str) -> str:
    """Get current time for a city."""
    loc = _geocode(city)
    if not loc:
        return f"Could not find city: {city}"

    tz = zoneinfo.ZoneInfo(loc.get("timezone", "UTC"))
    return f"{city}: {datetime.now(tz).strftime('%H:%M:%S %Z')}"


root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.5-flash",
    description="Agent to answer questions about the time and weather in a city.",
    instruction="You are a helpful agent who can answer user questions about the time and weather in a city.",
    tools=[get_weather, get_current_time],
)
