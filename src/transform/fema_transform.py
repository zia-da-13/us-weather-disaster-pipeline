import json
from datetime import datetime, timezone
from pathlib import Path


def get_latest_fema_file():
    """
    Find the most recent raw FEMA disaster JSON file.
    """

    project_root = Path(__file__).resolve().parents[2]

    raw_directory = (
        project_root
        / "data"
        / "raw"
        / "fema"
    )

    fema_files = list(
        raw_directory.glob("fema_disasters_*.json")
    )

    if not fema_files:
        print("No raw FEMA files found.")
        return None

    latest_file = max(
        fema_files,
        key=lambda file: file.stat().st_mtime
    )

    print(f"Latest FEMA file: {latest_file}")

    return latest_file


def load_fema_data(file_path):
    """
    Load raw FEMA disaster JSON data.
    """

    try:
        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:
            fema_data = json.load(file)

        print("Raw FEMA disaster data loaded successfully.")

        return fema_data

    except (OSError, json.JSONDecodeError) as error:
        print(f"Error loading FEMA data: {error}")
        return None


def transform_fema_data(fema_data):
    """
    Transform raw FEMA disaster data
    into clean disaster records.
    """

    if fema_data is None:
        return []

    disaster_records = fema_data.get(
        "DisasterDeclarationsSummaries",
        []
    )

    transformed_records = []

    for disaster in disaster_records:

        record = {
            "disaster_number": disaster.get(
                "disasterNumber"
            ),
            "state": disaster.get(
                "state"
            ),
            "declaration_type": disaster.get(
                "declarationType"
            ),
            "declaration_date": disaster.get(
                "declarationDate"
            ),
            "incident_type": disaster.get(
                "incidentType"
            ),
            "declaration_title": disaster.get(
                "declarationTitle"
            ),
            "incident_begin_date": disaster.get(
                "incidentBeginDate"
            ),
            "incident_end_date": disaster.get(
                "incidentEndDate"
            ),
            "fips_state_code": disaster.get(
                "fipsStateCode"
            ),
            "fips_county_code": disaster.get(
                "fipsCountyCode"
            ),
            "designated_area": disaster.get(
                "designatedArea"
            ),
            "place_code": disaster.get(
                "placeCode"
            ),
            "last_refresh": disaster.get(
                "lastRefresh"
            )
        }

        transformed_records.append(record)

    print(
        f"Transformed {len(transformed_records)} "
        f"FEMA disaster records."
    )

    return transformed_records


def save_transformed_fema_data(
    transformed_records
):
    """
    Save transformed FEMA records
    as a timestamped JSON file.
    """

    if not transformed_records:
        print("No transformed FEMA data to save.")
        return None

    project_root = Path(__file__).resolve().parents[2]

    output_directory = (
        project_root
        / "data"
        / "processed"
        / "fema"
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
        / f"fema_disasters_clean_{timestamp}.json"
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
                indent=4
            )

        print(
            f"Transformed FEMA disaster data saved to: "
            f"{output_file}"
        )

        return output_file

    except OSError as error:
        print(
            f"Error saving transformed FEMA data: "
            f"{error}"
        )
        return None


def main():
    """
    Run the FEMA transformation pipeline.
    """

    latest_file = get_latest_fema_file()

    if latest_file is None:
        return

    fema_data = load_fema_data(
        latest_file
    )

    if fema_data is None:
        return

    transformed_records = transform_fema_data(
        fema_data
    )

    save_transformed_fema_data(
        transformed_records
    )


if __name__ == "__main__":
    main()