"""Team report generator for analyzing team repositories and commits."""
from dataclasses import dataclass
from typing import Optional
from src.team.manager import TeamManager
from src.team.models import Team
from src.github.repository_client import GitHubRepositoryClient, RepositoryData


@dataclass
class TeamRepositoryReport:
    """Report containing team repository information and commit messages."""

    team: Team
    repository_name: Optional[str]
    commit_messages: list[str]
    found: bool


class TeamReportGenerator:
    """
    Generates reports for teams by finding their repositories and analyzing commits.

    The generator iterates through teams, finds repositories that contain all team member IDs,
    and collects commit messages from those repositories.
    """

    def __init__(self, team_manager: TeamManager, github_client: GitHubRepositoryClient) -> None:
        """
        Initialize the team report generator.

        Args:
            team_manager: TeamManager instance for accessing team data
            github_client: GitHubRepositoryClient instance for accessing GitHub data
        """
        self.team_manager = team_manager
        self.github_client = github_client

    def generate_reports(self) -> list[TeamRepositoryReport]:
        """
        Generate reports for all teams.

        For each team:
        1. Gets the first student ID from the team
        2. Searches for repositories containing that student ID
        3. Checks if repository name contains all other team member IDs
        4. Gets all commit messages from the matching repository

        Returns:
            List of TeamRepositoryReport objects, one per team

        Raises:
            ValueError: If organization name is not configured in github_client
        """
        reports: list[TeamRepositoryReport] = []

        for team in self.team_manager.iter_teams():
            report = self._generate_team_report(team)
            reports.append(report)

        return reports

    def _generate_team_report(self, team: Team) -> TeamRepositoryReport:
        """
        Generate report for a single team.

        Args:
            team: Team object to generate report for

        Returns:
            TeamRepositoryReport with repository and commit information
        """
        members = team.get_members()

        if not members:
            return TeamRepositoryReport(
                team=team,
                repository_name=None,
                commit_messages=[],
                found=False
            )

        # Step 1: Get first student ID
        first_student_id = members[0].student_id

        # Step 2: Search for repositories containing the first student ID
        try:
            repositories = self.github_client.search_repositories_by_name(first_student_id)
        except ValueError:
            # If search fails, return empty report
            return TeamRepositoryReport(
                team=team,
                repository_name=None,
                commit_messages=[],
                found=False
            )

        # Step 3: Find repository that contains all team member IDs
        team_repo = self._find_team_repository(team, repositories)

        if not team_repo:
            return TeamRepositoryReport(
                team=team,
                repository_name=None,
                commit_messages=[],
                found=False
            )

        # Step 4: Get all commit messages from the repository
        try:
            commit_messages = self.github_client.get_all_commit_messages(team_repo.name)
        except ValueError:
            # If getting commits fails, return report with empty messages
            return TeamRepositoryReport(
                team=team,
                repository_name=team_repo.name,
                commit_messages=[],
                found=True
            )

        return TeamRepositoryReport(
            team=team,
            repository_name=team_repo.name,
            commit_messages=commit_messages,
            found=True
        )

    def _find_team_repository(self, team: Team, repositories: list[RepositoryData]) -> Optional[RepositoryData]:
        """
        Find repository that contains all team member IDs in its name.

        Student IDs are typically separated by underscores in repository names.

        Args:
            team: Team object with member information
            repositories: List of RepositoryData objects to search through

        Returns:
            RepositoryData object if matching repository found, None otherwise
        """
        members = team.get_members()
        member_ids = [member.student_id for member in members]

        for repo in repositories:
            # Check if all member IDs are in the repository name
            if all(student_id in repo.name for student_id in member_ids):
                return repo

        return None
