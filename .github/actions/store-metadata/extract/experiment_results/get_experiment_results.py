import os
import glob
import csv
import re
from datetime import datetime
from loguru import logger


def get_experiment_results(absolute_path_to_repository):
    # get results for a specific version of the experiment

    # TODO - get units of data
    units_1 = "pkt_rate"
    unit_2 = "pkt_sz"

    # go to result > parse title of folder
    results_directory = os.path.join(absolute_path_to_repository, 'results')
    results = [
        name for name in os.listdir(results_directory)
        if os.path.isdir(os.path.join(results_directory, name))
    ]

    date_keys = []
    for result in results:
        date_keys.append(format_dir_date(result))

    # get results from data > [date] > tsv files with units
    data_files = []
    for key in date_keys:
        files = find_files_with_timestamp(absolute_path_to_repository, key)
        if files:  # Only extend if files list is not empty
            data_files.extend(files)


    meta = {}
    for file in data_files:
        relative_path = os.path.relpath(file, absolute_path_to_repository)
        match = re.search(r"pkt_sz-(\d+)", file)

        # if match:
        packet_size = match.group(1)
        # return None  # Return None if no match is found

        metadata = {
            "source_file": relative_path,
            "user": "gallenmuller",  # TODO
            # "date": datetime.strptime(timestamp[:6], "%y%m%d").date(),  # TODO
            # "time": datetime.strptime(timestamp[7:], "%H%M%S_%f").time(),  # TODO
            "packet_size": int(packet_size),
            "average_mpps": 0.01  # TODO - Interpreted from avg_mpps-001
        }

        data = []
        with open(file, "r") as file:
            reader = csv.reader(file, delimiter=' ')
            for row in reader:
                time_microseconds = int(row[0])
                measurement_value = float(row[1])

                # Convert time from microseconds to seconds
                time_seconds = time_microseconds / 1_000_000
                data.append({"time (s)": time_seconds, "value": measurement_value})

        metadata["data"] = data
        if packet_size not in meta:
            meta[packet_size] = []

        meta[packet_size].append(metadata)

    return meta


def find_files_with_timestamp(root_directory, timestamp):
    # Define the data directory path
    data_directory = os.path.join(root_directory, "data")

    # Construct the pattern to match files containing the timestamp
    pattern = f"*{timestamp}*"
    search_path = os.path.join(data_directory, pattern)

    # Use glob to find all matching files
    matching_files = glob.glob(search_path)

    # Check if any files were found
    if not matching_files:
        # raise FileNotFoundError(f"No files found with timestamp {timestamp} in {data_directory}")
        logger.warning(f"No files found with timestamp {timestamp} in {data_directory}")

    return matching_files or None


def format_dir_date(dir_date):
    # date = "2020-10-07_23-22-39_868017"
    # target_format = "20201007_232239_868017"

    # # Original date string
    # date = "2020-10-07_23-22-39_868017"
    # Define the input format
    input_format = "%Y-%m-%d_%H-%M-%S_%f"
    # Define the target format
    target_format = "%y%m%d_%H%M%S_%f"

    # Parse the date string into a datetime object
    datetime_obj = datetime.strptime(dir_date, input_format)

    # Format the datetime object into the target string format
    return datetime_obj.strftime(target_format)
