"""Data models for GitHubTracker."""
from typing import Optional
from dataclasses import dataclass


@dataclass
class Student:
    """Represents a student with their ID and full name."""

    student_id: str
    name: str

    def __str__(self) -> str:
        """Return string representation of student."""
        return f"{self.student_id} {self.name}"

    @classmethod
    def from_csv_field(cls, field: str) -> Optional['Student']:
        """
        Parse a student from CSV field with flexible format.

        The field can contain:
        - A student number (numeric ID)
        - One or more name parts (first name, last names)
        - Elements separated by spaces

        The student number is identified as the first numeric-only element.
        All other elements are combined to form the full name.

        Args:
            field: CSV field containing student information

        Returns:
            Student object if field is not empty, None otherwise

        Raises:
            ValueError: If no student ID (numeric) is found
        """
        field = field.strip()
        if not field:
            return None

        # Split by whitespace and clean up parts
        parts = field.split()
        parts = [part for part in parts if part]  # Remove empty parts

        if not parts:
            return None

        # Find student ID (first numeric element)
        student_id: Optional[str] = None
        name_parts: list[str] = []

        for part in parts:
            # Check if this part is purely numeric (student ID)
            if part.isdigit() and student_id is None:
                student_id = part
            else:
                name_parts.append(part)

        if student_id is None:
            raise ValueError(f"Invalid student format (no numeric ID found): {field}")

        if not name_parts:
            raise ValueError(f"Invalid student format (no name found): {field}")

        # Combine all name parts into a single name
        name = " ".join(name_parts)

        return cls(student_id=student_id, name=name)


@dataclass
class Team:
    """Represents a team with team number and 1-3 members."""

    team_number: str
    member1: Optional[Student]
    member2: Optional[Student]
    member3: Optional[Student]

    def __str__(self) -> str:
        """Return string representation of team."""
        members = []
        if self.member1:
            members.append(str(self.member1))
        if self.member2:
            members.append(str(self.member2))
        if self.member3:
            members.append(str(self.member3))

        members_str = " | ".join(members)
        return f"Team {self.team_number}: {members_str}"

    def get_members(self) -> list[Student]:
        """Return list of all non-None members."""
        members = []
        if self.member1:
            members.append(self.member1)
        if self.member2:
            members.append(self.member2)
        if self.member3:
            members.append(self.member3)
        return members

    def to_file_format(self) -> str:
        """
        Convert team to file format (one line per team).
        Format: team_number|member1|member2|member3
        Empty members are represented as empty strings.
        """
        m1 = str(self.member1) if self.member1 else ""
        m2 = str(self.member2) if self.member2 else ""
        m3 = str(self.member3) if self.member3 else ""
        return f"{self.team_number}|{m1}|{m2}|{m3}"

    @classmethod
    def from_file_format(cls, line: str) -> 'Team':
        """
        Parse team from file format.
        Format: team_number|member1|member2|member3

        Args:
            line: Line from file containing team information

        Returns:
            Team object
        """
        parts = line.strip().split('|')
        if len(parts) != 4:
            raise ValueError(f"Invalid team format: {line}")

        team_number = parts[0]
        member1 = Student.from_csv_field(parts[1]) if parts[1] else None
        member2 = Student.from_csv_field(parts[2]) if parts[2] else None
        member3 = Student.from_csv_field(parts[3]) if parts[3] else None

        return cls(
            team_number=team_number,
            member1=member1,
            member2=member2,
            member3=member3
        )
