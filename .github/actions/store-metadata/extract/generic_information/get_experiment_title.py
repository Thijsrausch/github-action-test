import git
from loguru import logger

def get_experiment_title(repo_path):
    """
    Retrieves the repository name.

    Parameters:
    - repo_path (str): The file system path to the local Git repository.

    Returns:
    - repo_name (str): The name of the repository.
    """
    try:
        repo = git.Repo(repo_path)
        remote_url = repo.remotes.origin.url
        # Extract the repository name from the URL
        repo_name = remote_url.split('/')[-1].replace('.git', '')
        return repo_name
    except Exception as e:
        logger.error(f"An error occurred while getting repository name: {e}")
        return None
