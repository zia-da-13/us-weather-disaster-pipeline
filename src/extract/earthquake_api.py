import json
from datetime import datetime
from pathlib import Path

import requests


USGS_EARTHQUAKE_URL = (
    "https://earthquake.usgs.gov/earthquakes/feed/v1.0/"
    "summary/all_day.geojson"
)


def extract_earthquake_data():
    """
    Extract earthquake data from the USGS GeoJSON feed.
    """

    print("Requesting earthquake data from USGS...")

    try:
        response = requests.get(
            USGS_EARTHQUAKE_URL,
            timeout=30
        )

        response.raise_for_status()

        earthquake_data = response.json()

        print("Earthquake data retrieved successfully.")

        return earthquake_data

    except requests.RequestException as error:
        print(f"Error retrieving earthquake data: {error}")
        return None


def save_raw_earthquake_data(earthquake_data):
    """
    Save raw USGS earthquake data as a timestamped JSON file.
    """

    if earthquake_data is None:
        print("No earthquake data available to save.")
        return None

    project_root = Path(__file__).resolve().parents[2]

    output_directory = (
        project_root
        / "data"
        / "raw"
        / "earthquakes"
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    output_file = (
        output_directory
        / f"earthquakes_{timestamp}.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            earthquake_data,
            file,
            indent=4
        )

    print(f"Raw earthquake data saved to: {output_file}")

    return output_file


def main():
    earthquake_data = extract_earthquake_data()

    if earthquake_data:
        earthquake_count = earthquake_data.get(
            "metadata",
            {}
        ).get(
            "count",
            0
        )

        print(
            f"Number of earthquakes retrieved: "
            f"{earthquake_count}"
        )

        save_raw_earthquake_data(
            earthquake_data
        )


if __name__ == "__main__":
    main()