import json
from datetime import datetime, timezone
from pathlib import Path


def get_latest_earthquake_file():
    """
    Find the most recent raw earthquake JSON file.
    """

    project_root = Path(__file__).resolve().parents[2]

    raw_directory = (
        project_root
        / "data"
        / "raw"
        / "earthquakes"
    )

    earthquake_files = list(
        raw_directory.glob("earthquakes_*.json")
    )

    if not earthquake_files:
        print("No raw earthquake files found.")
        return None

    latest_file = max(
        earthquake_files,
        key=lambda file: file.stat().st_mtime
    )

    print(f"Latest earthquake file: {latest_file}")

    return latest_file


def load_earthquake_data(file_path):
    """
    Load raw earthquake JSON data.
    """

    try:
        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:
            earthquake_data = json.load(file)

        print("Raw earthquake data loaded successfully.")

        return earthquake_data

    except (OSError, json.JSONDecodeError) as error:
        print(f"Error loading earthquake data: {error}")
        return None


def transform_earthquake_data(earthquake_data):
    """
    Transform raw USGS earthquake GeoJSON
    into a clean list of earthquake records.
    """

    if earthquake_data is None:
        return []

    transformed_records = []

    features = earthquake_data.get("features", [])

    for feature in features:

        properties = feature.get("properties", {})
        geometry = feature.get("geometry", {})
        coordinates = geometry.get("coordinates", [])

        longitude = None
        latitude = None
        depth_km = None

        if len(coordinates) >= 3:
            longitude = coordinates[0]
            latitude = coordinates[1]
            depth_km = coordinates[2]

        earthquake_time = properties.get("time")

        formatted_time = None

        if earthquake_time is not None:
            formatted_time = datetime.fromtimestamp(
                earthquake_time / 1000,
                tz=timezone.utc
            ).isoformat()

        record = {
            "earthquake_id": feature.get("id"),
            "magnitude": properties.get("mag"),
            "location": properties.get("place"),
            "event_time": formatted_time,
            "longitude": longitude,
            "latitude": latitude,
            "depth_km": depth_km,
            "tsunami": properties.get("tsunami"),
            "significance": properties.get("sig"),
            "status": properties.get("status"),
            "event_type": properties.get("type"),
            "detail_url": properties.get("url")
        }

        transformed_records.append(record)

    print(
        f"Transformed {len(transformed_records)} "
        f"earthquake records."
    )

    return transformed_records


def save_transformed_earthquake_data(
    transformed_records
):
    """
    Save transformed earthquake records
    as a JSON file.
    """

    if not transformed_records:
        print("No transformed earthquake data to save.")
        return None

    project_root = Path(__file__).resolve().parents[2]

    output_directory = (
        project_root
        / "data"
        / "processed"
        / "earthquakes"
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
        / f"earthquakes_clean_{timestamp}.json"
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
            f"Transformed earthquake data saved to: "
            f"{output_file}"
        )

        return output_file

    except OSError as error:
        print(
            f"Error saving transformed earthquake data: "
            f"{error}"
        )

        return None


def main():
    """
    Run the earthquake transformation pipeline.
    """

    latest_file = get_latest_earthquake_file()

    if latest_file is None:
        return

    earthquake_data = load_earthquake_data(
        latest_file
    )

    if earthquake_data is None:
        return

    transformed_records = transform_earthquake_data(
        earthquake_data
    )

    save_transformed_earthquake_data(
        transformed_records
    )


if __name__ == "__main__":
    main()