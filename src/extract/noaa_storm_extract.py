import gzip
import shutil
from datetime import datetime, timezone
from pathlib import Path

import requests


NOAA_BASE_URL = (
    "https://www.ncei.noaa.gov/pub/data/swdi/"
    "stormevents/csvfiles/"
)

DATA_YEAR = 2026


def find_latest_noaa_file():
    """
    Find the latest NOAA Storm Events details file
    for the selected year.
    """

    print(
        f"Searching NOAA Storm Events files for {DATA_YEAR}..."
    )

    try:
        response = requests.get(
            NOAA_BASE_URL,
            timeout=30
        )

        response.raise_for_status()

        page_content = response.text

        search_text = (
            f"StormEvents_details-ftp_v1.0_d{DATA_YEAR}_"
        )

        matching_files = []

        for line in page_content.splitlines():

            if search_text in line and ".csv.gz" in line:

                start = line.find(
                    "StormEvents_details-ftp"
                )

                end = line.find(
                    ".csv.gz",
                    start
                )

                if start != -1 and end != -1:

                    filename = line[
                        start:end + len(".csv.gz")
                    ]

                    matching_files.append(filename)

        matching_files = list(
            set(matching_files)
        )

        if not matching_files:
            print(
                f"No NOAA Storm Events file found "
                f"for {DATA_YEAR}."
            )
            return None

        latest_file = sorted(
            matching_files
        )[-1]

        print(
            f"Latest NOAA file found: {latest_file}"
        )

        return latest_file

    except requests.RequestException as error:
        print(
            f"Error searching NOAA files: {error}"
        )
        return None


def download_noaa_file(filename):
    """
    Download the NOAA compressed CSV file.
    """

    if filename is None:
        return None

    file_url = NOAA_BASE_URL + filename

    print("Downloading NOAA Storm Events data...")

    try:
        response = requests.get(
            file_url,
            timeout=60
        )

        response.raise_for_status()

        project_root = Path(
            __file__
        ).resolve().parents[2]

        output_directory = (
            project_root
            / "data"
            / "raw"
            / "noaa_storms"
        )

        output_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        timestamp = datetime.now(
            timezone.utc
        ).strftime("%Y%m%d_%H%M%S")

        compressed_file = (
            output_directory
            / f"noaa_storms_{DATA_YEAR}_{timestamp}.csv.gz"
        )

        with open(
            compressed_file,
            "wb"
        ) as file:
            file.write(response.content)

        print(
            f"Compressed NOAA file saved to: "
            f"{compressed_file}"
        )

        return compressed_file

    except requests.RequestException as error:
        print(
            f"Error downloading NOAA data: {error}"
        )
        return None


def extract_csv_file(compressed_file):
    """
    Decompress the NOAA .csv.gz file
    into a regular CSV file.
    """

    if compressed_file is None:
        return None

    csv_file = compressed_file.with_suffix("")

    try:
        with gzip.open(
            compressed_file,
            "rb"
        ) as source_file:

            with open(
                csv_file,
                "wb"
            ) as destination_file:

                shutil.copyfileobj(
                    source_file,
                    destination_file
                )

        print(
            f"NOAA CSV extracted to: {csv_file}"
        )

        return csv_file

    except OSError as error:
        print(
            f"Error extracting NOAA file: {error}"
        )
        return None


def main():
    """
    Run the NOAA Storm Events extraction pipeline.
    """

    filename = find_latest_noaa_file()

    if filename is None:
        return

    compressed_file = download_noaa_file(
        filename
    )

    if compressed_file is None:
        return

    csv_file = extract_csv_file(
        compressed_file
    )

    if csv_file is None:
        return

    print(
        "NOAA Storm Events extraction completed successfully."
    )


if __name__ == "__main__":
    main()