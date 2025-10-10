"""Tests for CSV parser module."""
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from src.team.csv_parser import TeamCSVParser
from src.team.models import Team, Student


class TestTeamCSVParser:
    """Test cases for TeamCSVParser class."""

    def test_parse_valid_csv_with_all_members(self, tmp_path: Path) -> None:
        """Test parsing a valid CSV file with all team members."""
        csv_file = tmp_path / "teams.csv"
        csv_content = """Team Number,Member 1,Member 2,Member 3
1,12345 Juan Pérez,67890 María García,11111 Carlos López
2,22222 Ana Martínez,33333 Luis Rodríguez,44444 Sofia Hernández"""
        csv_file.write_text(csv_content, encoding='utf-8')

        parser = TeamCSVParser(str(csv_file))
        teams = parser.parse()

        assert len(teams) == 2

        # Check team 1
        assert teams[0].team_number == "1"
        assert teams[0].member1 is not None
        assert teams[0].member1.student_id == "12345"
        assert teams[0].member1.name == "Juan Pérez"
        assert teams[0].member2 is not None
        assert teams[0].member2.student_id == "67890"
        assert teams[0].member2.name == "María García"
        assert teams[0].member3 is not None
        assert teams[0].member3.student_id == "11111"
        assert teams[0].member3.name == "Carlos López"

        # Check team 2
        assert teams[1].team_number == "2"
        assert teams[1].member1.student_id == "22222"
        assert teams[1].member2.student_id == "33333"
        assert teams[1].member3.student_id == "44444"

    def test_parse_csv_with_empty_members(self, tmp_path: Path) -> None:
        """Test parsing CSV with some empty member fields."""
        csv_file = tmp_path / "teams.csv"
        csv_content = """Team Number,Member 1,Member 2,Member 3
1,12345 Juan Pérez,,
2,22222 Ana Martínez,33333 Luis Rodríguez,"""
        csv_file.write_text(csv_content, encoding='utf-8')

        parser = TeamCSVParser(str(csv_file))
        teams = parser.parse()

        assert len(teams) == 2

        # Team 1: only member1
        assert teams[0].team_number == "1"
        assert teams[0].member1 is not None
        assert teams[0].member1.student_id == "12345"
        assert teams[0].member2 is None
        assert teams[0].member3 is None

        # Team 2: member1 and member2
        assert teams[1].team_number == "2"
        assert teams[1].member1 is not None
        assert teams[1].member2 is not None
        assert teams[1].member3 is None

    def test_parse_csv_skips_empty_team_rows(self, tmp_path: Path) -> None:
        """Test that rows with empty team numbers are skipped."""
        csv_file = tmp_path / "teams.csv"
        csv_content = """Team Number,Member 1,Member 2,Member 3
1,12345 Juan Pérez,,
,,33333 Luis Rodríguez,
2,22222 Ana Martínez,,"""
        csv_file.write_text(csv_content, encoding='utf-8')

        parser = TeamCSVParser(str(csv_file))
        teams = parser.parse()

        # Should only parse teams 1 and 2, skipping the empty team number row
        assert len(teams) == 2
        assert teams[0].team_number == "1"
        assert teams[1].team_number == "2"

    def test_parse_file_not_found(self, tmp_path: Path) -> None:
        """Test parsing a non-existent file raises FileNotFoundError."""
        csv_file = tmp_path / "nonexistent.csv"
        parser = TeamCSVParser(str(csv_file))

        with pytest.raises(FileNotFoundError, match="CSV file not found"):
            parser.parse()

    def test_parse_empty_csv_file(self, tmp_path: Path) -> None:
        """Test parsing an empty CSV file raises ValueError."""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("", encoding='utf-8')

        parser = TeamCSVParser(str(csv_file))

        with pytest.raises(ValueError, match="CSV file is empty"):
            parser.parse()

    def test_parse_csv_with_only_header(self, tmp_path: Path) -> None:
        """Test parsing CSV with only header returns empty list."""
        csv_file = tmp_path / "teams.csv"
        csv_content = """Team Number,Member 1,Member 2,Member 3"""
        csv_file.write_text(csv_content, encoding='utf-8')

        parser = TeamCSVParser(str(csv_file))
        teams = parser.parse()

        assert len(teams) == 0

    def test_parse_csv_with_insufficient_columns(self, tmp_path: Path) -> None:
        """Test parsing CSV with insufficient columns raises ValueError."""
        csv_file = tmp_path / "teams.csv"
        csv_content = """Team Number,Member 1,Member 2,Member 3
1,12345,Juan Pérez"""
        csv_file.write_text(csv_content, encoding='utf-8')

        parser = TeamCSVParser(str(csv_file))

        with pytest.raises(ValueError, match="Invalid row format at line 2: expected at least 4 columns"):
            parser.parse()

    def test_parse_csv_with_whitespace(self, tmp_path: Path) -> None:
        """Test parsing CSV properly handles whitespace in fields."""
        csv_file = tmp_path / "teams.csv"
        csv_content = """Team Number,Member 1,Member 2,Member 3
  1  ,  12345  Juan  Pérez  ,,"""
        csv_file.write_text(csv_content, encoding='utf-8')

        parser = TeamCSVParser(str(csv_file))
        teams = parser.parse()

        assert len(teams) == 1
        assert teams[0].team_number == "1"
        assert teams[0].member1 is not None
        assert teams[0].member1.student_id == "12345"
        assert teams[0].member1.name == "Juan Pérez"

    def test_parse_csv_with_special_characters(self, tmp_path: Path) -> None:
        """Test parsing CSV with special characters in names."""
        csv_file = tmp_path / "teams.csv"
        csv_content = """Team Number,Member 1,Member 2,Member 3
1,12345 José María Álvarez-García,,"""
        csv_file.write_text(csv_content, encoding='utf-8')

        parser = TeamCSVParser(str(csv_file))
        teams = parser.parse()

        assert len(teams) == 1
        assert teams[0].member1.name == "José María Álvarez-García"

    def test_parse_csv_multiple_teams(self, tmp_path: Path) -> None:
        """Test parsing CSV with multiple teams."""
        csv_file = tmp_path / "teams.csv"
        csv_content = """Team Number,Member 1,Member 2,Member 3
1,11111 Student One,,
2,22222 Student Two,33333 Student Three,
3,44444 Student Four,55555 Student Five,66666 Student Six
4,77777 Student Seven,,"""
        csv_file.write_text(csv_content, encoding='utf-8')

        parser = TeamCSVParser(str(csv_file))
        teams = parser.parse()

        assert len(teams) == 4
        assert teams[0].team_number == "1"
        assert teams[1].team_number == "2"
        assert teams[2].team_number == "3"
        assert teams[3].team_number == "4"

    def test_parse_csv_with_invalid_student_format(self, tmp_path: Path) -> None:
        """Test parsing CSV with invalid student format raises ValueError."""
        csv_file = tmp_path / "teams.csv"
        csv_content = """Team Number,Member 1,Member 2,Member 3
1,NoNumberHere Juan Pérez,,"""
        csv_file.write_text(csv_content, encoding='utf-8')

        parser = TeamCSVParser(str(csv_file))

        with pytest.raises(ValueError, match="Invalid student format"):
            parser.parse()

    def test_parser_initialization(self, tmp_path: Path) -> None:
        """Test parser initialization with different path types."""
        csv_file = tmp_path / "teams.csv"

        # Test with string path
        parser = TeamCSVParser(str(csv_file))
        assert parser.csv_path == csv_file

    def test_parse_csv_preserves_team_order(self, tmp_path: Path) -> None:
        """Test that parsing preserves the order of teams from CSV."""
        csv_file = tmp_path / "teams.csv"
        csv_content = """Team Number,Member 1,Member 2,Member 3
5,11111 Student,,
3,22222 Student,,
1,33333 Student,,
2,44444 Student,,"""
        csv_file.write_text(csv_content, encoding='utf-8')

        parser = TeamCSVParser(str(csv_file))
        teams = parser.parse()

        assert len(teams) == 4
        assert teams[0].team_number == "5"
        assert teams[1].team_number == "3"
        assert teams[2].team_number == "1"
        assert teams[3].team_number == "2"

    def test_parse_csv_with_semicolon_delimiter(self, tmp_path: Path) -> None:
        """Test parsing CSV with semicolon delimiter."""
        csv_file = tmp_path / "teams.csv"
        csv_content = """Team Number;Member 1;Member 2;Member 3
1;12345 Juan Pérez;67890 María García;11111 Carlos López
2;22222 Ana Martínez;33333 Luis Rodríguez;44444 Sofia Hernández"""
        csv_file.write_text(csv_content, encoding='utf-8')

        parser = TeamCSVParser(str(csv_file), delimiter=';')
        teams = parser.parse()

        assert len(teams) == 2
        assert teams[0].team_number == "1"
        assert teams[0].member1.student_id == "12345"
        assert teams[0].member1.name == "Juan Pérez"
        assert teams[1].team_number == "2"

    def test_parse_csv_with_bom(self, tmp_path: Path) -> None:
        """Test parsing CSV file with UTF-8 BOM."""
        csv_file = tmp_path / "teams.csv"
        csv_content = """Team Number,Member 1,Member 2,Member 3
1,12345 Juan Pérez,,"""
        # Write with BOM
        with open(csv_file, 'w', encoding='utf-8-sig') as f:
            f.write(csv_content)

        parser = TeamCSVParser(str(csv_file))
        teams = parser.parse()

        assert len(teams) == 1
        assert teams[0].team_number == "1"
