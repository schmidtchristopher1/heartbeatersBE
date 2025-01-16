import re
from flask import json
from typing import List


class Util:
    def check_email_address(email):
        return re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+" + "$", email)

    @staticmethod
    def data_reader(file_path):
        with open(file_path, "r") as file:
            data = file.read()
        return data.strip()

    @staticmethod
    def extract_heart_rate_values(file_path: str) -> dict:
        try:
            # Load and validate JSON data
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            # Get first entry and date
            first_entry = data[0]
            measurement_date = list(first_entry.keys())[0]  # Get the date

            # Extract heart rate values array
            heart_rate_values = first_entry[measurement_date]["heartRateValues"]

            # Get start time for relative time calculation
            start_time = heart_rate_values[0][0]  # First timestamp

            # Initialize arrays
            times = []
            values = []

            # Process each entry
            for entry in heart_rate_values:
                if entry[1] is not None:  # Check if value exists
                    # Convert to minutes from start
                    relative_time = (entry[0] - start_time) / (
                        1000 * 60
                    )  # Convert ms to minutes
                    times.append(round(relative_time, 2))
                    values.append(entry[1])

            return {
                "date_of_measurement": measurement_date,
                "time": times,
                "value": values,
                "metadata": {
                    "maxHeartRate": first_entry[measurement_date].get("maxHeartRate"),
                    "minHeartRate": first_entry[measurement_date].get("minHeartRate"),
                    "restingHeartRate": first_entry[measurement_date].get(
                        "restingHeartRate"
                    ),
                },
            }

        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")
            raise
