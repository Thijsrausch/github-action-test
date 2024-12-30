import os
from loguru import logger


def get_experiment_license(absolute_path_to_experiment):
    license_file_path = os.path.join(absolute_path_to_experiment, "LICENSE")

    if not os.path.isfile(absolute_path_to_experiment):
        logger.warning("LICENSE file not found in the repository")
        return

    with open(absolute_path_to_experiment, 'r') as file:
        first_line = file.readline().strip()

    relative_path = os.path.relpath(license_file_path, absolute_path_to_experiment)

    return {
        "license": first_line,
        "source": relative_path
    }
