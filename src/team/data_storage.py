"""Data storage for persisting team data to text file."""
from typing import List, Optional, Iterator
from pathlib import Path
from .models import Team


class TeamDataStorage:
    """Handles reading and writing team data to/from text file."""

    def __init__(self, storage_path: str) -> None:
        """
        Initialize data storage.

        Args:
            storage_path: Path to the storage text file
        """
        self.storage_path = Path(storage_path)

    def save_teams(self, teams: List[Team]) -> None:
        """
        Save teams to text file (one line per team).

        Args:
            teams: List of Team objects to save
        """
        # Create parent directory if it doesn't exist
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.storage_path, 'w', encoding='utf-8') as f:
            for team in teams:
                f.write(team.to_file_format() + '\n')

    def load_teams(self) -> List[Team]:
        """
        Load teams from text file.

        Returns:
            List of Team objects

        Raises:
            FileNotFoundError: If storage file doesn't exist
        """
        if not self.storage_path.exists():
            raise FileNotFoundError(f"Storage file not found: {self.storage_path}")

        teams: List[Team] = []
        with open(self.storage_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:  # Skip empty lines
                    team = Team.from_file_format(line)
                    teams.append(team)

        return teams

    def iter_teams(self) -> Iterator[Team]:
        """
        Iterate over teams in storage file without loading all into memory.

        Yields:
            Team objects one at a time

        Raises:
            FileNotFoundError: If storage file doesn't exist
        """
        if not self.storage_path.exists():
            raise FileNotFoundError(f"Storage file not found: {self.storage_path}")

        with open(self.storage_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:  # Skip empty lines
                    yield Team.from_file_format(line)

    def find_team_by_number(self, team_number: str) -> Optional[Team]:
        """
        Find a team by its team number.

        Args:
            team_number: Team number to search for

        Returns:
            Team object if found, None otherwise
        """
        if not self.storage_path.exists():
            return None

        for team in self.iter_teams():
            if team.team_number == team_number:
                return team

        return None

    def exists(self) -> bool:
        """Check if storage file exists."""
        return self.storage_path.exists()
