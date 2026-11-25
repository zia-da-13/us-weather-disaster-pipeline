
import json
import os
import sys
from pathlib import Path

import psycopg
from dotenv import load_dotenv


def get_project_root():
    """Return the project root directory."""

    return Path(__file__).resolve().parents[2]


def get_latest_weather_file():
    """Find the latest transformed weather JSON file."""

    project_root = get_project_root()

    processed_directory = (
        project_root / "data" / "processed" / "weather"
    )

    weather_files = list(
        processed_directory.glob("weather_clean_*.json")
    )

    if not weather_files:
        print("No transformed weather files found.")
        return None

    latest_file = max(
        weather_files,
        key=lambda file: file.stat().st_mtime
    )

    print(f"Latest weather file: {latest_file}")

    return latest_file


def load_weather_data(file_path):
    """Read transformed weather records from a JSON file."""

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        weather_records = json.load(file)

    if not isinstance(weather_records, list):
        raise ValueError("Invalid transformed weather JSON structure.")

    if not weather_records:
        raise ValueError("No weather records to load.")

    print(f"Loaded {len(weather_records)} weather records.")

    return weather_records


def load_weather_to_database(weather_records):
    """Insert or update weather forecast records in PostgreSQL."""

    project_root = get_project_root()

    load_dotenv(project_root / ".env")

    connection_settings = {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD")
    }

    insert_query = """
        INSERT INTO weather_forecasts (
            location,
            period_name,
            start_time,
            end_time,
            is_daytime,
            temperature,
            temperature_unit,
            precipitation_chance,
            wind_speed,
            wind_direction,
            short_forecast,
            detailed_forecast
        )
        VALUES (
            'Nashville, TN',
            %(period_name)s,
            %(start_time)s,
            %(end_time)s,
            %(is_daytime)s,
            %(temperature)s,
            %(temperature_unit)s,
            %(precipitation_chance)s,
            %(wind_speed)s,
            %(wind_direction)s,
            %(short_forecast)s,
            %(detailed_forecast)s
        )
        ON CONFLICT (location, start_time)
        DO UPDATE SET
            period_name = EXCLUDED.period_name,
            end_time = EXCLUDED.end_time,
            is_daytime = EXCLUDED.is_daytime,
            temperature = EXCLUDED.temperature,
            temperature_unit = EXCLUDED.temperature_unit,
            precipitation_chance = EXCLUDED.precipitation_chance,
            wind_speed = EXCLUDED.wind_speed,
            wind_direction = EXCLUDED.wind_direction,
            short_forecast = EXCLUDED.short_forecast,
            detailed_forecast = EXCLUDED.detailed_forecast;
    """

    with psycopg.connect(**connection_settings) as connection:

        with connection.cursor() as cursor:

            cursor.executemany(
                insert_query,
                weather_records
            )

    print(
        f"Successfully processed {len(weather_records)} "
        "weather records."
    )


def main():
    """Run the weather loading pipeline."""

    try:
        latest_file = get_latest_weather_file()

        if latest_file is None:
            print("Weather loading failed: no transformed file.")
            sys.exit(1)

        weather_records = load_weather_data(latest_file)

        for record in weather_records:

            if not isinstance(record, dict):
                raise ValueError("Invalid weather record structure.")

            start_time = record.get("start_time")

            if not isinstance(start_time, str) or not start_time.strip():
                raise ValueError(
                    "Weather record is missing start_time."
                )

        print(
            "Weather composite key validation "
            "completed successfully."
        )

        load_weather_to_database(weather_records)

        print("Weather loading completed successfully.")

    except (
        psycopg.Error,
        OSError,
        ValueError,
        TypeError,
        KeyError,
        AttributeError,
        OverflowError
    ) as error:

        print(f"Weather loading failed: {error}")

        sys.exit(1)


if __name__ == "__main__":
    main()
