
import json
from datetime import datetime, timezone
from pathlib import Path


def get_latest_weather_file():
    """Find the latest raw weather JSON file."""

    project_root = Path(__file__).resolve().parents[2]
    raw_directory = project_root / "data" / "raw" / "weather"

    weather_files = list(raw_directory.glob("weather_*.json"))

    if not weather_files:
        print("No raw weather files found.")
        return None

    latest_file = max(
        weather_files,
        key=lambda file: file.stat().st_mtime
    )

    print(f"Latest weather file: {latest_file}")
    return latest_file


def transform_weather_data(weather_data):
    """Transform weather forecast periods into clean records."""

    periods = weather_data.get("properties", {}).get("periods", [])
    transformed_records = []

    for period in periods:
        precipitation = period.get("probabilityOfPrecipitation") or {}

        record = {
            "period_name": period.get("name"),
            "start_time": period.get("startTime"),
            "end_time": period.get("endTime"),
            "is_daytime": period.get("isDaytime"),
            "temperature": period.get("temperature"),
            "temperature_unit": period.get("temperatureUnit"),
            "precipitation_chance": precipitation.get("value"),
            "wind_speed": period.get("windSpeed"),
            "wind_direction": period.get("windDirection"),
            "short_forecast": period.get("shortForecast"),
            "detailed_forecast": period.get("detailedForecast")
        }

        transformed_records.append(record)

    print(f"Transformed {len(transformed_records)} weather records.")
    return transformed_records


def save_transformed_weather_data(records):
    """Save transformed records to a JSON file."""

    if not records:
        print("No transformed weather data to save.")
        return None

    project_root = Path(__file__).resolve().parents[2]
    output_directory = project_root / "data" / "processed" / "weather"

    output_directory.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    output_file = (
        output_directory / f"weather_clean_{timestamp}.json"
    )

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=4)

    print(f"Transformed weather data saved to: {output_file}")
    return output_file


def main():
    """Run the weather transformation pipeline."""

    latest_file = get_latest_weather_file()

    if latest_file is None:
        return

    try:
        with open(latest_file, "r", encoding="utf-8") as file:
            weather_data = json.load(file)

        print("Raw weather data loaded successfully.")

        records = transform_weather_data(weather_data)
        save_transformed_weather_data(records)

    except (OSError, json.JSONDecodeError) as error:
        print(f"Weather transformation failed: {error}")


if __name__ == "__main__":
    main()
