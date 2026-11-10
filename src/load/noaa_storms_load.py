
import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import psycopg
from dotenv import load_dotenv


def get_project_root():
    return Path(__file__).resolve().parents[2]


def get_latest_noaa_file():
    processed_directory = (
        get_project_root() / "data" / "processed" / "noaa_storms"
    )

    noaa_files = list(processed_directory.glob("noaa_storms_clean_*.json"))

    if not noaa_files:
        print("No transformed NOAA Storm Events files found.")
        return None

    latest_file = max(noaa_files, key=lambda file: file.stat().st_mtime)
    print(f"Latest NOAA file: {latest_file}")

    return latest_file


def load_noaa_data(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        records = json.load(file)

    print(f"Loaded {len(records)} transformed NOAA records.")
    return records


def convert_datetime(value, timezone_code):
    if not value:
        return None

    parsed_date = datetime.strptime(value, "%d-%b-%y %H:%M:%S")

    if not timezone_code:
        return None

    timezone_code = timezone_code.strip().upper()

    # Guam Standard Time is UTC+10.
    if timezone_code == "GST10":
        return parsed_date.replace(
            tzinfo=timezone(timedelta(hours=10))
        )

    # Handle NOAA timezone codes such as EST-5 and CST-6.
    match = re.fullmatch(
        r"[A-Z]+([+-]\d{1,2})",
        timezone_code
    )

    if match:
        hours = int(match.group(1))

        return parsed_date.replace(
            tzinfo=timezone(timedelta(hours=hours))
        )

    # Leave unknown timezones as NULL instead of guessing.
    return None


def prepare_records(records):
    prepared_records = []

    for record in records:
        prepared_record = record.copy()

        prepared_record["begin_date_time"] = convert_datetime(
            record.get("begin_date_time"),
            record.get("timezone"),
        )

        prepared_record["end_date_time"] = convert_datetime(
            record.get("end_date_time"),
            record.get("timezone"),
        )

        prepared_records.append(prepared_record)

    return prepared_records


def load_noaa_to_database(records):
    load_dotenv(get_project_root() / ".env")

    connection_settings = {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }

    columns = [
        "episode_id",
        "event_id",
        "year",
        "month",
        "state",
        "state_fips",
        "event_type",
        "county_zone_type",
        "county_zone_fips",
        "county_zone_name",
        "weather_forecast_office",
        "begin_date_time",
        "end_date_time",
        "timezone",
        "injuries_direct",
        "injuries_indirect",
        "deaths_direct",
        "deaths_indirect",
        "property_damage_usd",
        "crop_damage_usd",
        "source",
        "magnitude",
        "magnitude_type",
        "flood_cause",
        "tornado_scale",
        "tornado_length",
        "tornado_width",
        "begin_location",
        "end_location",
        "begin_latitude",
        "begin_longitude",
        "end_latitude",
        "end_longitude",
        "episode_narrative",
        "event_narrative",
    ]

    column_names = ", ".join(columns)

    placeholders = ", ".join(
        f"%({column})s" for column in columns
    )

    update_columns = [
        column for column in columns if column != "event_id"
    ]

    update_clause = ", ".join(
        f"{column} = EXCLUDED.{column}"
        for column in update_columns
    )

    insert_query = f"""
        INSERT INTO noaa_storms ({column_names})
        VALUES ({placeholders})
        ON CONFLICT (event_id)
        DO UPDATE SET {update_clause};
    """

    batch_size = 1000

    with psycopg.connect(**connection_settings) as connection:
        with connection.cursor() as cursor:
            for start in range(0, len(records), batch_size):
                batch = records[start:start + batch_size]

                cursor.executemany(insert_query, batch)

                print(
                    f"Processed {min(start + batch_size, len(records))}"
                    f" / {len(records)} records."
                )

    print(f"Successfully processed {len(records)} NOAA records.")


def main():
    latest_file = get_latest_noaa_file()

    if latest_file is None:
        return

    try:
        records = load_noaa_data(latest_file)

        if not records:
            print("No NOAA records to load.")
            return

        prepared_records = prepare_records(records)

        load_noaa_to_database(prepared_records)

        print("NOAA Storm Events loading completed successfully.")

    except (psycopg.Error, OSError, ValueError, TypeError) as error:
        print(f"NOAA loading failed: {error}")


if __name__ == "__main__":
    main()
