
import json
import sys
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
    """
    Retrieve weather forecast data from the NWS API.
    """

    point_url = f"{BASE_URL}/points/{LATITUDE},{LONGITUDE}"

    try:
        print("Requesting Nashville weather data from NWS...")

        point_response = requests.get(
            point_url,
            headers=HEADERS,
            timeout=30
        )

        point_response.raise_for_status()

        point_data = point_response.json()

        forecast_url = point_data["properties"]["forecast"]

        if not isinstance(forecast_url, str) or not forecast_url:
            print("No valid NWS forecast URL found.")
            return None

        print(f"NWS forecast URL: {forecast_url}")

        forecast_response = requests.get(
            forecast_url,
            headers=HEADERS,
            timeout=30
        )

        forecast_response.raise_for_status()

        forecast_data = forecast_response.json()

        periods = forecast_data["properties"]["periods"]

        if not isinstance(periods, list) or not periods:
            print("No valid NWS forecast periods found.")
            return None

        print("NWS weather data retrieved successfully.")

        return forecast_data

    except (
        requests.RequestException,
        ValueError,
        KeyError,
        TypeError
    ) as error:
        print(f"Error retrieving NWS weather data: {error}")
        return None


def save_raw_weather_data(weather_data):
    """
    Save raw NWS weather data as a timestamped JSON file.
    """

    if not weather_data:
        print("No weather data available to save.")
        return None

    project_root = Path(__file__).resolve().parents[2]

    raw_data_folder = (
        project_root
        / "data"
        / "raw"
        / "weather"
    )

    timestamp = datetime.now().strftime(
        "%Y_%m_%d_%H%M%S"
    )

    file_name = f"weather_{timestamp}.json"

    file_path = raw_data_folder / file_name

    temporary_file = file_path.with_suffix(".json.tmp")

    try:
        raw_data_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            temporary_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                weather_data,
                file,
                indent=4
            )

        temporary_file.replace(file_path)

        print(f"\nRaw weather data saved to: {file_path}")

        return file_path

    except (OSError, ValueError, TypeError) as error:
        print(f"Error saving NWS weather data: {error}")

        temporary_file.unlink(missing_ok=True)

        return None


def transform_weather_data(weather_data):
    """
    Prepare weather forecast records for display.
    """

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
    """
    Display Nashville weather forecast records.
    """

    print("\nNASHVILLE WEATHER FORECAST")
    print("=" * 50)

    for record in weather_records:

        print(f"\nPeriod: {record['period_name']}")

        print(
            f"Temperature: "
            f"{record['temperature']} "
            f"{record['temperature_unit']}"
        )

        precipitation_chance = record["precipitation_chance"]

        if precipitation_chance is None:
            print("Precipitation Chance: Not available")
        else:
            print(
                f"Precipitation Chance: "
                f"{precipitation_chance}%"
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


def main():
    """
    Run the NWS weather extraction process.
    """

    try:
        weather_data = get_weather_forecast()

        if weather_data is None:
            print("NWS weather extraction failed.")
            sys.exit(1)

        weather_records = transform_weather_data(
            weather_data
        )

        if not weather_records:
            print("No NWS weather forecast records found.")
            sys.exit(1)

        print(
            f"Number of NWS forecast periods retrieved: "
            f"{len(weather_records)}"
        )

        output_file = save_raw_weather_data(
            weather_data
        )

        if output_file is None:
            print("NWS weather data saving failed.")
            sys.exit(1)

        display_weather_records(
            weather_records
        )

        print(
            "\nNWS weather extraction completed successfully."
        )

    except (
        OSError,
        ValueError,
        TypeError,
        KeyError,
        AttributeError
    ) as error:
        print(f"NWS weather extraction failed: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
