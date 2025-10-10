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

    def test_search_repositories_by_name_returns_matching_repos(self):
        """Test searching repositories in organization by name fragment."""
        # Arrange
        client = GitHubRepositoryClient(org_name="python")
        search_term = "python"

        # Act
        results = client.search_repositories_by_name(search_term)

        # Assert
        assert isinstance(results, list)
        assert len(results) > 0
        # All results should contain the search term in their name (case insensitive)
        for repo in results:
            assert isinstance(repo, RepositoryData)
            assert search_term.lower() in repo.name.lower()

    def test_search_repositories_by_name_with_no_matches_returns_empty_list(self):
        """Test searching with non-matching term returns empty list."""
        # Arrange
        client = GitHubRepositoryClient(org_name="python")
        search_term = "nonexistent-repo-xyz-12345"

        # Act
        results = client.search_repositories_by_name(search_term)

        # Assert
        assert isinstance(results, list)
        assert len(results) == 0

    def test_search_repositories_uses_org_from_environment(self):
        """Test that search uses organization from environment variable."""
        # Arrange
        import os
        original_org = os.environ.get("GITHUB_ORG")
        os.environ["GITHUB_ORG"] = "python"

        try:
            client = GitHubRepositoryClient()  # Should use GITHUB_ORG env var
            search_term = "cpython"

            # Act
            results = client.search_repositories_by_name(search_term)

            # Assert
            assert len(results) > 0
            assert any(repo.name == "cpython" for repo in results)
        finally:
            # Cleanup
            if original_org:
                os.environ["GITHUB_ORG"] = original_org
            else:
                os.environ.pop("GITHUB_ORG", None)
