
import json
import sys
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

    if not isinstance(weather_data, dict):
        raise ValueError("Invalid weather JSON structure.")

    properties = weather_data.get("properties")

    if not isinstance(properties, dict):
        raise ValueError("Invalid weather properties.")

    periods = properties.get("periods")

    if not isinstance(periods, list) or not periods:
        raise ValueError("No valid weather forecast periods found.")

    transformed_records = []

    for period in periods:

        if not isinstance(period, dict):
            raise ValueError("Invalid weather forecast record.")

        start_time = period.get("startTime")

        if not isinstance(start_time, str) or not start_time.strip():
            raise ValueError("Weather record is missing start_time.")

        precipitation = (
            period.get("probabilityOfPrecipitation") or {}
        )

        if not isinstance(precipitation, dict):
            raise ValueError("Invalid precipitation data.")

        record = {
            "period_name": period.get("name"),
            "start_time": start_time,
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

    print(
        f"Transformed {len(transformed_records)} weather records."
    )

    return transformed_records


def save_transformed_weather_data(records):
    """Save transformed records to a JSON file."""

    if not records:
        print("No transformed weather data to save.")
        return None

    project_root = Path(__file__).resolve().parents[2]

    output_directory = (
        project_root / "data" / "processed" / "weather"
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%d_%H%M%S"
    )

    output_file = (
        output_directory / f"weather_clean_{timestamp}.json"
    )

    temporary_file = output_file.with_suffix(".json.tmp")

    try:
        with open(
            temporary_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                records,
                file,
                indent=4
            )

        temporary_file.replace(output_file)

    except (OSError, ValueError, TypeError):

        temporary_file.unlink(missing_ok=True)

        raise

    print(f"Transformed weather data saved to: {output_file}")

    return output_file


def main():
    """Run the weather transformation pipeline."""

    try:
        latest_file = get_latest_weather_file()

        if latest_file is None:
            print("Weather transformation failed: no raw file.")
            sys.exit(1)

        with open(
            latest_file,
            "r",
            encoding="utf-8"
        ) as file:

            weather_data = json.load(file)

        print("Raw weather data loaded successfully.")

        records = transform_weather_data(weather_data)

        if not records:
            print("No transformed weather records found.")
            sys.exit(1)

        output_file = save_transformed_weather_data(records)

        if output_file is None:
            print("Weather transformation saving failed.")
            sys.exit(1)

        print("Weather transformation completed successfully.")

    except (
        OSError,
        ValueError,
        TypeError,
        KeyError,
        AttributeError
    ) as error:

        print(f"Weather transformation failed: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
