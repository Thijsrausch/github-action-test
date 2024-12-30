import os
import json
from loguru import logger


def get_manual_metadata(directory):
    """
    Looks for 'metadata.json' in the given directory. If found,
    opens the file and returns its contents as a dictionary.

    Parameters:
        directory (str): The directory to search in.

    Returns:
        dict: The contents of 'metadata.json' as a dictionary if the file exists.
        None: If 'metadata.json' does not exist in the directory.
    """
    metadata_path = os.path.join(directory, 'metadata.json')
    if os.path.isfile(metadata_path):
        with open(metadata_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    else:
        logger.info(f"No 'metadata.json' file found in the directory: {directory}")
        return None
