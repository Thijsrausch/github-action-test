import subprocess
import re


def get_github_username(repo_path):
    try:
        # Run git command to get the remote URL
        result = subprocess.run(
            ["git", "-C", repo_path, "remote", "get-url", "origin"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        remote_url = result.stdout.strip()

        # Match GitHub username in the URL format
        match = re.search(r'github\.com[:/](.+?)/', remote_url)
        if match:
            return match.group(1)
        else:
            raise ValueError("GitHub username not found in remote URL.")
    except subprocess.CalledProcessError:
        raise ValueError("Failed to get the remote URL. Ensure the path is a valid Git repository.")
