import os
from utils.get_github_username import get_github_username


def get_repository_documentation_url(absolute_path_to_experiment):
    # Extract repository name from the path
    repo_name = os.path.basename(absolute_path_to_experiment.rstrip('/'))
    # Replace 'your-username' with the GitHub username associated with this repo
    user_name = get_github_username(absolute_path_to_experiment)

    # Construct the GitHub Pages URL for the gh-pages branch
    return f"https://{user_name}.github.io/{repo_name}"
