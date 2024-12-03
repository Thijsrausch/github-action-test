import json
import os
import pymongo


def store_metadata_in_mongodb():
    # Retrieve environment variables
    mongo_uri = os.getenv('MONGO_URI')
    database_name = os.getenv('DATABASE_NAME')
    collection_name = os.getenv('COLLECTION_NAME')
    metadata_file_path = 'metadata.json'

    # Connect to MongoDB
    client = pymongo.MongoClient(mongo_uri)
    db = client[database_name]
    collection = db[collection_name]

    # Check if metadata.json exists
    if not os.path.exists(metadata_file_path):
        print(f"File '{metadata_file_path}' not found in the repository.")
        return

    # Read and insert metadata
    with open(metadata_file_path, 'r') as file:
        metadata = json.load(file)
        collection.insert_one(metadata)
        print(f"Inserted metadata into MongoDB collection '{collection_name}'.")


if __name__ == "__main__":
    store_metadata_in_mongodb()
