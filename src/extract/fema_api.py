
import json
import sys
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

        if not isinstance(fema_data, dict):
            print("Invalid FEMA API response format.")
            return None

        disaster_records = fema_data.get(
            "DisasterDeclarationsSummaries"
        )

        if not isinstance(disaster_records, list):
            print("Invalid FEMA disaster records format.")
            return None

        if not disaster_records:
            print("FEMA API returned no disaster records.")
            return None

        print("FEMA disaster data retrieved successfully.")

        return fema_data

    except (requests.RequestException, ValueError) as error:
        print(f"Error retrieving FEMA data: {error}")
        return None


def save_raw_fema_data(fema_data):
    """
    Save raw FEMA disaster data as a timestamped JSON file.
    """

    if not fema_data:
        print("No FEMA data available to save.")
        return None

    project_root = Path(__file__).resolve().parents[2]

    output_directory = (
        project_root
        / "data"
        / "raw"
        / "fema"
    )

    timestamp = datetime.now(
        timezone.utc
    ).strftime("%Y%m%d_%H%M%S")

    output_file = (
        output_directory
        / f"fema_disasters_{timestamp}.json"
    )

    temporary_file = output_file.with_suffix(".json.tmp")

    try:
        output_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            temporary_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                fema_data,
                file,
                indent=4
            )

        temporary_file.replace(output_file)

        print(
            f"Raw FEMA disaster data saved to: "
            f"{output_file}"
        )

        return output_file

    except (OSError, ValueError, TypeError) as error:
        print(
            f"Error saving FEMA disaster data: "
            f"{error}"
        )

        temporary_file.unlink(missing_ok=True)

        return None


def main():
    """
    Run the FEMA extraction process.
    """

    try:
        fema_data = extract_fema_data()

        if fema_data is None:
            print("FEMA extraction failed.")
            sys.exit(1)

        disaster_records = fema_data.get(
            "DisasterDeclarationsSummaries",
            []
        )

        print(
            f"Number of FEMA disaster records retrieved: "
            f"{len(disaster_records)}"
        )

        output_file = save_raw_fema_data(
            fema_data
        )

        if output_file is None:
            print("FEMA data saving failed.")
            sys.exit(1)

        print(
            "FEMA disaster extraction completed successfully."
        )

    except (OSError, ValueError, TypeError) as error:
        print(f"FEMA extraction failed: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
