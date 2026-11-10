
import json
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv


def get_project_root():
    return Path(__file__).resolve().parents[2]


def get_latest_fema_file():
    project_root = get_project_root()
    processed_directory = project_root / "data" / "processed" / "fema"

    fema_files = list(
        processed_directory.glob("fema_disasters_clean_*.json")
    )

    if not fema_files:
        print("No transformed FEMA files found.")
        return None

    latest_file = max(
        fema_files,
        key=lambda file: file.stat().st_mtime
    )

    print(f"Latest FEMA file: {latest_file}")
    return latest_file


def load_fema_data(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        fema_records = json.load(file)

    print(f"Loaded {len(fema_records)} transformed FEMA records.")
    return fema_records


def load_fema_to_database(fema_records):
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
        INSERT INTO fema_disasters (
            disaster_number,
            state,
            declaration_type,
            declaration_date,
            incident_type,
            declaration_title,
            incident_begin_date,
            incident_end_date,
            fips_state_code,
            fips_county_code,
            designated_area,
            place_code,
            last_refresh
        )
        VALUES (
            %(disaster_number)s,
            %(state)s,
            %(declaration_type)s,
            %(declaration_date)s,
            %(incident_type)s,
            %(declaration_title)s,
            %(incident_begin_date)s,
            %(incident_end_date)s,
            %(fips_state_code)s,
            %(fips_county_code)s,
            %(designated_area)s,
            %(place_code)s,
            %(last_refresh)s
        )
        ON CONFLICT (disaster_number, state, place_code)
        DO UPDATE SET
            declaration_type = EXCLUDED.declaration_type,
            declaration_date = EXCLUDED.declaration_date,
            incident_type = EXCLUDED.incident_type,
            declaration_title = EXCLUDED.declaration_title,
            incident_begin_date = EXCLUDED.incident_begin_date,
            incident_end_date = EXCLUDED.incident_end_date,
            fips_state_code = EXCLUDED.fips_state_code,
            fips_county_code = EXCLUDED.fips_county_code,
            designated_area = EXCLUDED.designated_area,
            last_refresh = EXCLUDED.last_refresh;
    """

    with psycopg.connect(**connection_settings) as connection:
        with connection.cursor() as cursor:
            cursor.executemany(insert_query, fema_records)

    print(f"Successfully processed {len(fema_records)} FEMA records.")


def main():
    latest_file = get_latest_fema_file()

    if latest_file is None:
        return

    try:
        fema_records = load_fema_data(latest_file)

        if not fema_records:
            print("No FEMA records to load.")
            return

        unique_fields = (
            "disaster_number",
            "state",
            "place_code"
        )

        for record in fema_records:
            if any(record.get(field) is None for field in unique_fields):
                print("FEMA loading stopped: missing unique key value.")
                return

        load_fema_to_database(fema_records)
        print("FEMA loading completed successfully.")

    except (psycopg.Error, OSError, ValueError, TypeError) as error:
        print(f"FEMA loading failed: {error}")


if __name__ == "__main__":
    main()
