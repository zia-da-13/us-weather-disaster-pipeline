import json
from datetime import datetime, timezone
from pathlib import Path

import requests


FEMA_API_URL = (
    "https://www.fema.gov/api/open/v2/"
    "DisasterDeclarationsSummaries"
)


def extract_fema_data():
    """
    Extract disaster declaration data from FEMA OpenFEMA.
    """

    print("Requesting disaster data from FEMA...")

    parameters = {
        "$top": 1000,
        "$orderby": "declarationDate desc"
    }

    try:
        response = requests.get(
            FEMA_API_URL,
            params=parameters,
            timeout=30
        )

        response.raise_for_status()

        fema_data = response.json()

        print("FEMA disaster data retrieved successfully.")

        return fema_data

    except requests.RequestException as error:
        print(f"Error retrieving FEMA data: {error}")
        return None


def save_raw_fema_data(fema_data):
    """
    Save raw FEMA disaster data as a timestamped JSON file.
    """

    if fema_data is None:
        print("No FEMA data available to save.")
        return None

    project_root = Path(__file__).resolve().parents[2]

    output_directory = (
        project_root
        / "data"
        / "raw"
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
        / f"fema_disasters_{timestamp}.json"
    )

    try:
        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                fema_data,
                file,
                indent=4
            )

        print(
            f"Raw FEMA disaster data saved to: "
            f"{output_file}"
        )

        return output_file

    except OSError as error:
        print(
            f"Error saving FEMA disaster data: "
            f"{error}"
        )

        return None


def main():
    """
    Run the FEMA extraction process.
    """

    fema_data = extract_fema_data()

    if fema_data is None:
        return

    disaster_records = fema_data.get(
        "DisasterDeclarationsSummaries",
        []
    )

    print(
        f"Number of FEMA disaster records retrieved: "
        f"{len(disaster_records)}"
    )

    save_raw_fema_data(
        fema_data
    )


if __name__ == "__main__":
    main()