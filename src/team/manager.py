"""Team manager for accessing and managing team data."""
from typing import List, Optional, Iterator
from .models import Team
from .csv_parser import TeamCSVParser
from .data_storage import TeamDataStorage


class TeamManager:
    """
    Main class for accessing team data with iteration methods.
    Provides high-level interface for team operations.
    """

    def __init__(self, storage_path: str = "teams_data.txt") -> None:
        """
        Initialize team manager.

        Args:
            storage_path: Path to the storage file
        """
        self.storage = TeamDataStorage(storage_path)

    def load_from_csv(self, csv_path: str, delimiter: str = ',') -> None:
        """
        Load teams from CSV file and save to storage.

        Args:
            csv_path: Path to the CSV file
            delimiter: CSV delimiter character (default: ',')

        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If CSV format is invalid
        """
        parser = TeamCSVParser(csv_path, delimiter=delimiter)
        teams = parser.parse()
        self.storage.save_teams(teams)

    def get_all_teams(self) -> List[Team]:
        """
        Get all teams from storage.

        Returns:
            List of all Team objects
        """
        return self.storage.load_teams()

    def iter_teams(self) -> Iterator[Team]:
        """
        Iterate over teams without loading all into memory.

        Yields:
            Team objects one at a time
        """
        return self.storage.iter_teams()

    def find_team(self, team_number: str) -> Optional[Team]:
        """
        Find a team by its team number.

        Args:
            team_number: Team number to search for

        Returns:
            Team object if found, None otherwise
        """
        return self.storage.find_team_by_number(team_number)

    def has_data(self) -> bool:
        """Check if storage file exists with data."""
        return self.storage.exists()
