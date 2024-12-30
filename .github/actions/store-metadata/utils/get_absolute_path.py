import os
from loguru import logger


def get_absolute_path(relative_path):
    absolute_path = os.path.abspath(relative_path)

    if not os.path.isdir(absolute_path):
        logger.error(f"The provided path {absolute_path} is not a valid directory.")
        raise ValueError(f"The provided path {absolute_path} is not a valid directory.")

    return absolute_path
