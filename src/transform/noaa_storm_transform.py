import csv
import json
from datetime import datetime, timezone
from pathlib import Path


def get_latest_noaa_file():
    """
    Find the most recent raw NOAA Storm Events CSV file.
    """

    project_root = Path(__file__).resolve().parents[2]

    raw_directory = (
        project_root
        / "data"
        / "raw"
        / "noaa_storms"
    )

    noaa_files = list(
        raw_directory.glob("noaa_storms_*.csv")
    )

    if not noaa_files:
        print("No raw NOAA Storm Events CSV files found.")
        return None

    latest_file = max(
        noaa_files,
        key=lambda file: file.stat().st_mtime
    )

    print(f"Latest NOAA file: {latest_file}")

    return latest_file


def load_noaa_data(file_path):
    """
    Load NOAA Storm Events CSV data.
    """

    records = []

    try:
        with open(
            file_path,
            "r",
            encoding="utf-8",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:
                records.append(row)

        print(
            f"Loaded {len(records)} NOAA storm records."
        )

        return records

    except (OSError, csv.Error) as error:
        print(f"Error loading NOAA data: {error}")
        return []


def convert_to_integer(value):
    """
    Convert a value to an integer when possible.
    """

    if value is None or value == "":
        return None

    try:
        return int(value)

    except ValueError:
        return None


def convert_to_float(value):
    """
    Convert a value to a float when possible.
    """

    if value is None or value == "":
        return None

    try:
        return float(value)

    except ValueError:
        return None


def convert_damage_value(value):
    """
    Convert NOAA damage values such as:
    1.00K, 10.00K, 2.50M

    into numeric dollar values.
    """

    if value is None:
        return None

    value = value.strip().upper()

    if value == "":
        return None

    multiplier = 1

    if value.endswith("K"):
        multiplier = 1_000
        value = value[:-1]

    elif value.endswith("M"):
        multiplier = 1_000_000
        value = value[:-1]

    elif value.endswith("B"):
        multiplier = 1_000_000_000
        value = value[:-1]

    try:
        return float(value) * multiplier

    except ValueError:
        return None


def transform_noaa_data(noaa_records):
    """
    Transform raw NOAA Storm Events records
    into clean analysis-ready records.
    """

    transformed_records = []

    for storm in noaa_records:

        record = {
            "episode_id": convert_to_integer(
                storm.get("EPISODE_ID")
            ),
            "event_id": convert_to_integer(
                storm.get("EVENT_ID")
            ),
            "year": convert_to_integer(
                storm.get("YEAR")
            ),
            "month": storm.get("MONTH_NAME"),
            "state": storm.get("STATE"),
            "state_fips": storm.get("STATE_FIPS"),
            "event_type": storm.get("EVENT_TYPE"),
            "county_zone_type": storm.get("CZ_TYPE"),
            "county_zone_fips": storm.get("CZ_FIPS"),
            "county_zone_name": storm.get("CZ_NAME"),
            "weather_forecast_office": storm.get("WFO"),
            "begin_date_time": storm.get(
                "BEGIN_DATE_TIME"
            ),
            "end_date_time": storm.get(
                "END_DATE_TIME"
            ),
            "timezone": storm.get("CZ_TIMEZONE"),
            "injuries_direct": convert_to_integer(
                storm.get("INJURIES_DIRECT")
            ),
            "injuries_indirect": convert_to_integer(
                storm.get("INJURIES_INDIRECT")
            ),
            "deaths_direct": convert_to_integer(
                storm.get("DEATHS_DIRECT")
            ),
            "deaths_indirect": convert_to_integer(
                storm.get("DEATHS_INDIRECT")
            ),
            "property_damage_usd": convert_damage_value(
                storm.get("DAMAGE_PROPERTY")
            ),
            "crop_damage_usd": convert_damage_value(
                storm.get("DAMAGE_CROPS")
            ),
            "source": storm.get("SOURCE"),
            "magnitude": convert_to_float(
                storm.get("MAGNITUDE")
            ),
            "magnitude_type": storm.get(
                "MAGNITUDE_TYPE"
            ),
            "flood_cause": storm.get("FLOOD_CAUSE"),
            "tornado_scale": storm.get("TOR_F_SCALE"),
            "tornado_length": convert_to_float(
                storm.get("TOR_LENGTH")
            ),
            "tornado_width": convert_to_float(
                storm.get("TOR_WIDTH")
            ),
            "begin_location": storm.get(
                "BEGIN_LOCATION"
            ),
            "end_location": storm.get(
                "END_LOCATION"
            ),
            "begin_latitude": convert_to_float(
                storm.get("BEGIN_LAT")
            ),
            "begin_longitude": convert_to_float(
                storm.get("BEGIN_LON")
            ),
            "end_latitude": convert_to_float(
                storm.get("END_LAT")
            ),
            "end_longitude": convert_to_float(
                storm.get("END_LON")
            ),
            "episode_narrative": storm.get(
                "EPISODE_NARRATIVE"
            ),
            "event_narrative": storm.get(
                "EVENT_NARRATIVE"
            )
        }

        transformed_records.append(record)

    print(
        f"Transformed {len(transformed_records)} "
        f"NOAA storm records."
    )

    return transformed_records


def save_transformed_noaa_data(
    transformed_records
):
    """
    Save transformed NOAA Storm Events data
    as a timestamped JSON file.
    """

    if not transformed_records:
        print("No transformed NOAA data to save.")
        return None

    project_root = Path(__file__).resolve().parents[2]

    output_directory = (
        project_root
        / "data"
        / "processed"
        / "noaa_storms"
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now(
        timezone.utc
    ).strftime("%Y%m%d_%H%M%S")

    output_file = (
        output_directory
        / f"noaa_storms_clean_{timestamp}.json"
    )

    try:
        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                transformed_records,
                file,
                indent=4,
                ensure_ascii=False
            )

        print(
            f"Transformed NOAA storm data saved to: "
            f"{output_file}"
        )

        return output_file

    except OSError as error:
        print(
            f"Error saving transformed NOAA data: "
            f"{error}"
        )

        return None


def main():
    """
    Run the NOAA Storm Events transformation pipeline.
    """

    latest_file = get_latest_noaa_file()

    if latest_file is None:
        return

    noaa_records = load_noaa_data(
        latest_file
    )

    if not noaa_records:
        return

    transformed_records = transform_noaa_data(
        noaa_records
    )

    save_transformed_noaa_data(
        transformed_records
    )


if __name__ == "__main__":
    main()