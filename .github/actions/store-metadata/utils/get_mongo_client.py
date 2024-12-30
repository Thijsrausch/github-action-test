from pymongo import MongoClient
from loguru import logger


def get_mongo_client(host, port):
    if not isinstance(port, int):
        try:
            port = int(port)
        except ValueError:
            logger.error("The string is not a valid integer.")

    return MongoClient(host, port)
