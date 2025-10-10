"""Tests for GitHub repository client."""
import pytest
from src.github.repository_client import GitHubRepositoryClient, RepositoryData


class TestGitHubRepositoryClient:
    """Test cases for GitHubRepositoryClient class."""

    def test_get_repository_returns_repository_data(self):
        """Test getting repository data returns RepositoryData object with correct fields."""
        # Arrange
        client = GitHubRepositoryClient()
        org_name = "python"
        repo_name = "cpython"

        # Act
        result = client.get_repository(org_name, repo_name)

        # Assert
        assert isinstance(result, RepositoryData)
        assert result.name == repo_name
        assert result.full_name == f"{org_name}/{repo_name}"
        assert result.description is not None
        assert isinstance(result.stars, int)
        assert result.stars >= 0
        assert isinstance(result.forks, int)
        assert result.forks >= 0
        assert result.url == f"https://github.com/{org_name}/{repo_name}"

    def test_get_repository_with_invalid_repo_raises_error(self):
        """Test getting non-existent repository raises ValueError."""
        # Arrange
        client = GitHubRepositoryClient()
        org_name = "nonexistent-org-12345"
        repo_name = "nonexistent-repo-12345"

        # Act & Assert
        with pytest.raises(ValueError, match="Repository not found"):
            client.get_repository(org_name, repo_name)
