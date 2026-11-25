
import json
import os
import sys
from pathlib import Path

import psycopg
from dotenv import load_dotenv


def get_project_root():
    return Path(__file__).resolve().parents[2]


def get_latest_earthquake_file():
    project_root = get_project_root()
    processed_directory = project_root / "data" / "processed" / "earthquakes"

    earthquake_files = list(
        processed_directory.glob("earthquakes_clean_*.json")
    )

    if not earthquake_files:
        print("No transformed earthquake files found.")
        return None

    latest_file = max(
        earthquake_files,
        key=lambda file: file.stat().st_mtime
    )

    print(f"Latest earthquake file: {latest_file}")
    return latest_file


def load_earthquake_data(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        earthquake_records = json.load(file)

    print(f"Loaded {len(earthquake_records)} transformed earthquake records.")
    return earthquake_records


def load_earthquakes_to_database(earthquake_records):
    project_root = get_project_root()
    load_dotenv(project_root / ".env")

    connection_settings = {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }

    insert_query = """
        INSERT INTO earthquakes (
            earthquake_id,
            magnitude,
            location,
            event_time,
            longitude,
            latitude,
            depth_km,
            tsunami,
            significance,
            status,
            event_type,
            detail_url
        )
        VALUES (
            %(earthquake_id)s,
            %(magnitude)s,
            %(location)s,
            %(event_time)s,
            %(longitude)s,
            %(latitude)s,
            %(depth_km)s,
            %(tsunami)s,
            %(significance)s,
            %(status)s,
            %(event_type)s,
            %(detail_url)s
        )
        ON CONFLICT (earthquake_id)
        DO UPDATE SET
            magnitude = EXCLUDED.magnitude,
            location = EXCLUDED.location,
            event_time = EXCLUDED.event_time,
            longitude = EXCLUDED.longitude,
            latitude = EXCLUDED.latitude,
            depth_km = EXCLUDED.depth_km,
            tsunami = EXCLUDED.tsunami,
            significance = EXCLUDED.significance,
            status = EXCLUDED.status,
            event_type = EXCLUDED.event_type,
            detail_url = EXCLUDED.detail_url;
    """

    with psycopg.connect(**connection_settings) as connection:
        with connection.cursor() as cursor:
            cursor.executemany(insert_query, earthquake_records)

    print(f"Successfully processed {len(earthquake_records)} earthquake records.")


def main():
    try:
        latest_file = get_latest_earthquake_file()

        if latest_file is None:
            print("Earthquake loading failed.")
            sys.exit(1)

        earthquake_records = load_earthquake_data(latest_file)

        if not isinstance(earthquake_records, list):
            print("Invalid earthquake data format.")
            sys.exit(1)

        if not earthquake_records:
            print("No earthquake records to load.")
            sys.exit(1)

        for record in earthquake_records:
            if not isinstance(record, dict) or not record.get("earthquake_id"):
                print("Invalid or missing earthquake ID.")
                sys.exit(1)

        load_earthquakes_to_database(earthquake_records)

        print("Earthquake loading completed successfully.")

    except (
        psycopg.Error,
        OSError,
        ValueError,
        TypeError
    ) as error:
        print(f"Earthquake loading failed: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
