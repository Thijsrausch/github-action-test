def get_experiment_by_name(client, db_name, collection_name, experiment_name):
    db = client[db_name]
    collection = db[collection_name]

    result = collection.find_one({"experiment_name": experiment_name})

    return result if result else None
