import git
from collections import Counter
from loguru import logger

def get_experiment_contributors(repo_path):
    """
    Retrieves author name, email, and number of commits for each author.

    Parameters:
    - repo_path (str): The file system path to the local Git repository.

    Returns:
    - contributors (list): A list of dictionaries with name, email, and commit count for each author.
    """
    try:
        repo = git.Repo(repo_path)
        commits = list(repo.iter_commits())
        authors = [(commit.author.name, commit.author.email) for commit in commits]
        author_count = Counter(authors)

        contributors = [
            {"name": name, "email": email, "commits": count}
            for (name, email), count in author_count.items()
        ]

        return contributors

    except Exception as e:
        logger.error(f"An error occurred while getting author info: {e}")
        return None
