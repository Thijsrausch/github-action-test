import json
from loguru import logger


def generate_json(dictionary, title):
    try:
        filename = f"{title}.json"
        # Convert the dictionary to a JSON string
        json_data = json.dumps(dictionary, ensure_ascii=False, indent=4)

        # Save the JSON data to a file
        with open(filename, 'w') as json_file:
            json_file.write(json_data)

        logger.info(f"JSON file has been generated and saved as {filename}")

        return filename

    except Exception as e:
        logger.error(f"An error occurred while generating JSON: {e}")
