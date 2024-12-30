from pymongo import MongoClient
# from loguru import logger


def get_mongo_client(mongo_uri):
    # if not isinstance(port, int):
    #     try:
    #         port = int(port)
    #     except ValueError:
    #         logger.error("The string is not a valid integer.")

    return MongoClient(mongo_uri)
