import sys
from datetime import date
from loguru import logger
from dotenv import load_dotenv
import os

from extract.generic_information.get_experiment_contributors import get_experiment_contributors
from extract.generic_information.get_experiment_license import get_experiment_license
from extract.generic_information.get_experiment_title import get_experiment_title
from extract.generic_information.get_experiment_versions import get_experiment_version
from extract.generic_information.get_last_updated_date import get_last_updated_date
from extract.generic_information.get_manual_metadata import get_manual_metadata
from extract.generic_information.get_readme import parse_readme
from extract.generic_information.get_repository_documentation_url import get_repository_documentation_url
from extract.generic_information.get_repository_url import get_repository_url
from extract.experiment_results.get_experiment_results import get_experiment_results
from extract.experiment.get_experiment import get_experiment
from utils.generate_json import generate_json
from utils.get_absolute_path import get_absolute_path
from utils.get_experiment_by_name import get_experiment_by_name
from utils.get_mongo_client import get_mongo_client
from utils.insert_file_to_collection import insert_json_to_mongodb

load_dotenv()

host = os.getenv("HOST")
port = os.getenv("PORT")
database_name = os.getenv("DATABASE_NAME")
current_collection_name = os.getenv("CURRENT_COLLECTION_NAME")


def extract_metadata_from_pos_experiment(absolute_path_to_experiment, metadata=None):
    now = date.today().isoformat()
    if metadata is None:
        # we need to create this field only when the metadata is created
        metadata = {"created_at": now}

    metadata["updated_at"] = now

    readme = parse_readme(absolute_path_to_experiment)
    metadata["readme"] = readme if readme else None

    repository_url = get_repository_url(absolute_path_to_experiment)
    metadata["repository_url"] = repository_url if repository_url else None

    documentation_url = get_repository_documentation_url(absolute_path_to_experiment)
    metadata["documentation_url"] = documentation_url if documentation_url else None

    contributors = get_experiment_contributors(absolute_path_to_experiment)
    metadata["contributors"] = contributors if contributors else None

    code_updated_at, last_commit_sha = get_last_updated_date(absolute_path_to_experiment)
    metadata["code_updated_at"] = code_updated_at if code_updated_at else None
    metadata["last_commit_sha"] = last_commit_sha if last_commit_sha else None  # make into dict

    version = get_experiment_version(absolute_path_to_experiment)
    metadata["version"] = version if version else None

    experiment_license = get_experiment_license(absolute_path_to_experiment)
    metadata["license"] = experiment_license if experiment_license else None

    experiment_metadata = get_experiment(absolute_path_to_experiment)
    metadata["experiment"] = experiment_metadata if experiment_metadata else None

    experiment_results = get_experiment_results(absolute_path_to_experiment)
    metadata["experiment_results"] = experiment_results if experiment_results else None

    manual_metadata = get_manual_metadata(absolute_path_to_experiment)
    metadata["manual_metadata"] = manual_metadata if manual_metadata else None

    return metadata


if __name__ == "__main__":
    if len(sys.argv) != 2:
        logger.error("Usage: python main.py <relative_path_to_experiment>")
        sys.exit(1)

    relative_path_to_experiment = sys.argv[1]

    absolute_path_to_experiment = get_absolute_path(relative_path_to_experiment)

    experiment_name = get_experiment_title(absolute_path_to_experiment)

    client = get_mongo_client(host, port)

    experiment = get_experiment_by_name(client, database_name, current_collection_name, experiment_name)

    metadata = extract_metadata_from_pos_experiment(absolute_path_to_experiment)
    metadata["experiment_name"] = experiment_name if experiment_name else None

    metadata_json_file_name = generate_json(metadata, experiment_name)

    insert_json_to_mongodb(client, experiment, metadata_json_file_name, database_name, current_collection_name)

    client.close()
