import os
from loguru import logger


def get_experiment_version(absolute_path_to_experiment):
    version_file_path = os.path.join(absolute_path_to_experiment, "VERSION")

    try:
        with open(version_file_path, "r") as version_file:
            version = version_file.read().strip()
        return version
    except FileNotFoundError:
        logger.warning(f"No VERSION file found in the specified repository path: {absolute_path_to_experiment}")
        return None
    except Exception as e:
        logger.error(f"An error occurred while reading the VERSION file: {e}")
        raise RuntimeError(f"An error occurred while reading the VERSION file: {e}")
