"""Main entry point for GitHubTracker application."""
from src.team import TeamManager
from src.ui import ConsoleUI


def main() -> None:
    """Main function to run the application."""
    # Initialize team manager with default storage file
    team_manager = TeamManager(storage_path="teams_data.txt")

    # Create and run console UI
    ui = ConsoleUI(team_manager)
    ui.run()


if __name__ == "__main__":
    main()
