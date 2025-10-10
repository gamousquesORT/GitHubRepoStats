"""GitHub repository client for accessing repository data."""
from dataclasses import dataclass
from typing import Optional
import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class RepositoryData:
    """Data class representing a GitHub repository."""

    name: str
    full_name: str
    description: Optional[str]
    stars: int
    forks: int
    url: str


class GitHubRepositoryClient:
    """Client for accessing GitHub repository information."""

    def __init__(self, token: Optional[str] = None, base_url: Optional[str] = None, org_name: Optional[str] = None) -> None:
        """
        Initialize GitHub repository client.

        Args:
            token: Optional GitHub personal access token for authentication.
                   If not provided, reads from GITHUB_TOKEN environment variable.
            base_url: Optional GitHub API base URL.
                     If not provided, reads from GITHUB_API_URL environment variable,
                     or defaults to https://api.github.com
            org_name: Optional GitHub organization name.
                     If not provided, reads from GITHUB_ORG environment variable.
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.base_url = base_url or os.getenv("GITHUB_API_URL", "https://api.github.com")
        self.org_name = org_name or os.getenv("GITHUB_ORG")

        self.session = requests.Session()
        if self.token:
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    def get_repository(self, org_name: str, repo_name: str) -> RepositoryData:
        """
        Get repository data from GitHub API.

        Args:
            org_name: Organization name
            repo_name: Repository name

        Returns:
            RepositoryData object with repository information

        Raises:
            ValueError: If repository is not found or API request fails
        """
        url = f"{self.base_url}/repos/{org_name}/{repo_name}"

        try:
            response = self.session.get(url)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Repository not found: {org_name}/{repo_name}")
            raise ValueError(f"GitHub API error: {e}")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to connect to GitHub API: {e}")

        data = response.json()

        return RepositoryData(
            name=data["name"],
            full_name=data["full_name"],
            description=data.get("description"),
            stars=data["stargazers_count"],
            forks=data["forks_count"],
            url=data["html_url"]
        )

    def search_repositories_by_name(self, search_term: str) -> list[RepositoryData]:
        """
        Search for repositories in the organization that contain the search term in their name.

        Args:
            search_term: The term to search for in repository names (case insensitive)

        Returns:
            List of RepositoryData objects for repositories matching the search term

        Raises:
            ValueError: If organization name is not configured or API request fails
        """
        if not self.org_name:
            raise ValueError("Organization name not configured. Set GITHUB_ORG environment variable or pass org_name to constructor.")

        url = f"{self.base_url}/orgs/{self.org_name}/repos"

        try:
            # Get all repositories from the organization (with pagination support)
            all_repos: list[RepositoryData] = []
            page = 1
            per_page = 100

            while True:
                params = {"page": page, "per_page": per_page}
                response = self.session.get(url, params=params)
                response.raise_for_status()

                repos_data = response.json()

                if not repos_data:
                    break

                # Filter repositories by search term
                for repo in repos_data:
                    if search_term.lower() in repo["name"].lower():
                        all_repos.append(RepositoryData(
                            name=repo["name"],
                            full_name=repo["full_name"],
                            description=repo.get("description"),
                            stars=repo["stargazers_count"],
                            forks=repo["forks_count"],
                            url=repo["html_url"]
                        ))

                page += 1

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Organization not found: {self.org_name}")
            raise ValueError(f"GitHub API error: {e}")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to connect to GitHub API: {e}")

        return all_repos
