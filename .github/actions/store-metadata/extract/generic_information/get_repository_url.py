import git
from loguru import logger

def get_repository_url(repo_path):
    """
    Retrieves the remote URL of the repository.

    Parameters:
    - repo_path (str): The file system path to the local Git repository.

    Returns:
    - remote_url (str): The remote URL of the repository.
    """
    try:
        repo = git.Repo(repo_path)
        remote_url = repo.remotes.origin.url
        return remote_url
    except Exception as e:
        logger.error(f"An error occurred while getting repository URL: {e}")
        return None
