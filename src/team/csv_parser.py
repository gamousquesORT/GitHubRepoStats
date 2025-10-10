"""CSV parser for reading team data."""
import csv
from typing import List
from pathlib import Path
from .models import Team, Student


class TeamCSVParser:
    """Parser for reading team data from CSV files."""

    def __init__(self, csv_path: str, delimiter: str = ',') -> None:
        """
        Initialize CSV parser.

        Args:
            csv_path: Path to the CSV file
            delimiter: CSV delimiter character (default: ',')
        """
        self.csv_path = Path(csv_path)
        self.delimiter = delimiter

    def parse(self) -> List[Team]:
        """
        Parse CSV file and return list of Team objects.

        Returns:
            List of Team objects

        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If CSV format is invalid
        """
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")

        teams: List[Team] = []

        with open(self.csv_path, 'r', encoding='utf-8-sig') as csvfile:
            reader = csv.reader(csvfile, delimiter=self.delimiter)

            # Skip header row
            header = next(reader, None)
            if header is None:
                raise ValueError("CSV file is empty")

            # Process each data row
            for row_number, row in enumerate(reader, start=2):
                if len(row) < 4:
                    raise ValueError(
                        f"Invalid row format at line {row_number}: expected at least 4 columns"
                    )

                team_number = row[0].strip()
                if not team_number:
                    # Skip rows with empty team number
                    continue

                # Parse members (can be empty)
                member1 = Student.from_csv_field(row[1]) if row[1].strip() else None
                member2 = Student.from_csv_field(row[2]) if row[2].strip() else None
                member3 = Student.from_csv_field(row[3]) if row[3].strip() else None

                team = Team(
                    team_number=team_number,
                    member1=member1,
                    member2=member2,
                    member3=member3
                )
                teams.append(team)

        return teams
