import json
from datetime import datetime
from pathlib import Path

import requests


BASE_URL = "https://api.weather.gov"

# Nashville, Tennessee coordinates
LATITUDE = 36.1627
LONGITUDE = -86.7816

HEADERS = {
    "User-Agent": "us-weather-disaster-pipeline"
}


def get_weather_forecast():
    point_url = f"{BASE_URL}/points/{LATITUDE},{LONGITUDE}"

    point_response = requests.get(
        point_url,
        headers=HEADERS,
        timeout=30
    )

    point_response.raise_for_status()

    point_data = point_response.json()

    forecast_url = point_data["properties"]["forecast"]

    forecast_response = requests.get(
        forecast_url,
        headers=HEADERS,
        timeout=30
    )

    forecast_response.raise_for_status()

    forecast_data = forecast_response.json()

    return forecast_data


def save_raw_weather_data(weather_data):
    raw_data_folder = Path("data/raw/weather")

    raw_data_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y_%m_%d_%H%M%S"
    )

    file_name = f"weather_{timestamp}.json"

    file_path = raw_data_folder / file_name

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            weather_data,
            file,
            indent=4
        )

    print(f"\nRaw weather data saved to: {file_path}")


def transform_weather_data(weather_data):
    periods = weather_data["properties"]["periods"]

    weather_records = []

    for period in periods:
        record = {
            "period_name": period["name"],
            "start_time": period["startTime"],
            "end_time": period["endTime"],
            "is_daytime": period["isDaytime"],
            "temperature": period["temperature"],
            "temperature_unit": period["temperatureUnit"],
            "precipitation_chance": (
                period["probabilityOfPrecipitation"]["value"]
            ),
            "wind_speed": period["windSpeed"],
            "wind_direction": period["windDirection"],
            "short_forecast": period["shortForecast"],
            "detailed_forecast": period["detailedForecast"]
        }

        weather_records.append(record)

    return weather_records


def display_weather_records(weather_records):
    print("\nNASHVILLE WEATHER FORECAST")
    print("=" * 50)

    for record in weather_records:
        print(f"\nPeriod: {record['period_name']}")

        print(
            f"Temperature: "
            f"{record['temperature']} "
            f"{record['temperature_unit']}"
        )

        print(
            f"Precipitation Chance: "
            f"{record['precipitation_chance']}%"
        )

        print(
            f"Wind: "
            f"{record['wind_speed']} "
            f"{record['wind_direction']}"
        )

        print(
            f"Forecast: "
            f"{record['short_forecast']}"
        )

        print("-" * 50)


if __name__ == "__main__":
    weather_data = get_weather_forecast()

    save_raw_weather_data(weather_data)

    weather_records = transform_weather_data(
        weather_data
    )

    display_weather_records(
        weather_records
    )