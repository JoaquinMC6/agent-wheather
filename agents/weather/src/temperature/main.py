"""
Weather Agent - Given a city, outputs the current temperature and the forecast for the next week.
Uses Microsoft Agent Framework with Azure AI Foundry and Open-Meteo API.
Ready for deployment to Foundry Hosted Agent service.
"""

import os
from typing import Annotated

import httpx
from agent_framework import Agent, tool
from agent_framework.foundry import FoundryChatClient
from agent_framework_foundry_hosting import ResponsesHostServer
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv(override=True)

PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
MODEL_DEPLOYMENT_NAME = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")

if not PROJECT_ENDPOINT:
    raise SystemExit(
        "Error: PROJECT_ENDPOINT environment variable is not set.\n"
        "Copy .env.sample to .env and fill in your Azure AI Foundry project endpoint."
    )

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def _geocode_city(city: str) -> dict | None:
    try:
        response = httpx.get(GEOCODING_URL, params={"name": city, "count": 1}, timeout=10)
        response.raise_for_status()
        results = response.json().get("results")
        if not results:
            return None
        return results[0]
    except Exception:
        return None


@tool
def get_current_temperature(
    city: Annotated[str, "Name of the city to get the current temperature for"],
) -> str:
    """
    Get the current temperature in the specified city.
    Returns the temperature in Celsius along with basic location info.
    """
    geo = _geocode_city(city)
    if not geo:
        return f"Error: Could not find the city '{city}'. Please check the spelling and try again."

    try:
        response = httpx.get(
            FORECAST_URL,
            params={
                "latitude": geo["latitude"],
                "longitude": geo["longitude"],
                "current": "temperature_2m",
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        current = data["current"]
        temp = current["temperature_2m"]
        unit = data["current_units"]["temperature_2m"]
        location_name = geo.get("name", city)
        country = geo.get("country", "")
        return f"Current temperature in {location_name}, {country}: {temp}°{unit}"
    except Exception as e:
        return f"Error fetching current temperature for '{city}': {e}"


@tool
def get_weekly_temperature_forecast(
    city: Annotated[str, "Name of the city to get the weekly temperature forecast for"],
) -> str:
    """
    Get the temperature forecast for the next 7 days in the specified city.
    Returns daily minimum and maximum temperatures in Celsius.
    """
    geo = _geocode_city(city)
    if not geo:
        return f"Error: Could not find the city '{city}'. Please check the spelling and try again."

    try:
        response = httpx.get(
            FORECAST_URL,
            params={
                "latitude": geo["latitude"],
                "longitude": geo["longitude"],
                "daily": "temperature_2m_max,temperature_2m_min",
                "forecast_days": 7,
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        daily = data["daily"]
        dates = daily["time"]
        max_temps = daily["temperature_2m_max"]
        min_temps = daily["temperature_2m_min"]
        unit = data["daily_units"]["temperature_2m_max"]
        location_name = geo.get("name", city)
        country = geo.get("country", "")

        result = f"7-day temperature forecast for {location_name}, {country}:\n\n"
        for date, t_max, t_min in zip(dates, max_temps, min_temps):
            result += f"  {date}: {t_min}°{unit} - {t_max}°{unit}\n"
        return result
    except Exception as e:
        return f"Error fetching weekly forecast for '{city}': {e}"


def main():
    """Main function to run the agent as a web server."""

    client = FoundryChatClient(
        project_endpoint=PROJECT_ENDPOINT,
        model=MODEL_DEPLOYMENT_NAME,
        credential=DefaultAzureCredential(),
    )

    agent = Agent(
        client=client,
        name="WeatherAgent",
        instructions="""You are a helpful weather assistant that provides current temperature and weekly forecast information for any city.

When a user asks about the weather or temperature in a city:
1. Identify the city name from the user's request
2. Use the get_current_temperature tool to fetch the current temperature
3. Use the get_weekly_temperature_forecast tool to fetch the 7-day forecast
4. Present both results in a friendly, clear way
5. Offer to help with additional questions

Be conversational and helpful. If users ask about things unrelated to weather,
politely let them know you specialize in weather and temperature information.""",
        tools=[get_current_temperature, get_weekly_temperature_forecast],
    )

    print("Weather Agent Server running on http://localhost:8088")
    server = ResponsesHostServer(agent)
    server.run()


if __name__ == "__main__":
    main()
