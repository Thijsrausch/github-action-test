import git
from loguru import logger

def get_last_updated_date(repo_path):
    """
    Retrieves the date and commit ID (SHA) of the last commit.

    Parameters:
    - repo_path (str): The file system path to the local Git repository.

    Returns:
    - last_commit_date (str): The date of the last commit.
    - last_commit_sha (str): The commit ID (SHA) of the last commit.
    """
    try:
        repo = git.Repo(repo_path)
        last_commit = next(repo.iter_commits(max_count=1))
        last_commit_date = last_commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S')
        last_commit_sha = last_commit.hexsha
        return last_commit_date, last_commit_sha
    except Exception as e:
        logger.error(f"An error occurred while getting last commit info: {e}")
        return None, None
