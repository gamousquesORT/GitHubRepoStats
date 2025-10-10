"""Main entry point for GitHubTracker application."""
from src.team import TeamManager
from src.ui import ConsoleUI
from src.github.repository_client import GitHubRepositoryClient


def main() -> None:
    """Main function to run the application."""
    # Initialize team manager with default storage file
    team_manager = TeamManager(storage_path="teams_data.txt")

    # Initialize GitHub client (will use environment variables for configuration)
    github_client = GitHubRepositoryClient()

    # Create and run console UI with GitHub client
    ui = ConsoleUI(team_manager, github_client)
    ui.run()


if __name__ == "__main__":
    main()
