"""Tests for TeamReportGenerator class."""
import pytest
from src.reports.team_report_generator import TeamReportGenerator, TeamRepositoryReport
from src.team.models import Team, Student
from src.team.manager import TeamManager
from src.github.repository_client import GitHubRepositoryClient


class TestTeamReportGenerator:
    """Test cases for TeamReportGenerator class."""

    def test_generate_reports_returns_list_of_reports(self):
        """Test that generate_reports returns a list of TeamRepositoryReport objects."""
        # Arrange
        team_manager = TeamManager("tests/reports/test_teams.txt")
        # Create test data
        team = Team(
            team_number="1",
            member1=Student("12345", "John Doe"),
            member2=Student("67890", "Jane Smith"),
            member3=None
        )
        team_manager.storage.save_teams([team])

        github_client = GitHubRepositoryClient(org_name="test-org")
        generator = TeamReportGenerator(team_manager, github_client)

        # Act
        reports = generator.generate_reports()

        # Assert
        assert isinstance(reports, list)

    def test_find_team_repository_returns_matching_repo(self):
        """Test finding repository that contains all team member IDs."""
        # Arrange
        github_client = GitHubRepositoryClient(org_name="octocat")
        generator = TeamReportGenerator(TeamManager(), github_client)

        team = Team(
            team_number="1",
            member1=Student("12345", "John Doe"),
            member2=Student("67890", "Jane Smith"),
            member3=None
        )

        # Mock repositories (in real test this would use test data)
        repos = [
            type('obj', (object,), {'name': 'project-12345-67890', 'full_name': 'octocat/project-12345-67890'}),
            type('obj', (object,), {'name': 'other-project', 'full_name': 'octocat/other-project'})
        ]

        # Act
        result = generator._find_team_repository(team, repos)

        # Assert
        assert result is not None
        assert "12345" in result.name
        assert "67890" in result.name

    def test_team_repository_report_contains_expected_fields(self):
        """Test that TeamRepositoryReport dataclass has expected structure."""
        # Arrange
        team = Team(
            team_number="1",
            member1=Student("12345", "John Doe"),
            member2=None,
            member3=None
        )
        repo_name = "test-repo-12345"
        commit_messages = ["Initial commit", "Add feature"]

        # Act
        report = TeamRepositoryReport(
            team=team,
            repository_name=repo_name,
            commit_messages=commit_messages,
            found=True
        )

        # Assert
        assert report.team == team
        assert report.repository_name == repo_name
        assert report.commit_messages == commit_messages
        assert report.found is True
