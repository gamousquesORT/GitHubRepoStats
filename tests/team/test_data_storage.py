"""Unit tests for TeamDataStorage class."""
import unittest
import tempfile
import os
from pathlib import Path
from src.team import Student, Team, TeamDataStorage


class TestTeamDataStorage(unittest.TestCase):
    """Test cases for TeamDataStorage class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.storage_path = os.path.join(self.test_dir, "test_teams.txt")
        self.storage = TeamDataStorage(self.storage_path)

        # Create sample teams for testing
        self.team1 = Team(
            team_number="1",
            member1=Student("12345", "Juan Pérez"),
            member2=Student("67890", "María García"),
            member3=Student("11223", "Carlos López")
        )
        self.team2 = Team(
            team_number="2",
            member1=Student("44556", "Ana Martínez"),
            member2=Student("77889", "Pedro Sánchez"),
            member3=None
        )
        self.team3 = Team(
            team_number="3",
            member1=Student("99001", "Laura Fernández"),
            member2=None,
            member3=None
        )

    def tearDown(self):
        """Clean up test files after each test method."""
        # Remove test file if it exists
        if os.path.exists(self.storage_path):
            os.remove(self.storage_path)
        # Remove test directory
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)

    def test_save_teams_creates_file(self):
        """Test that save_teams creates a file."""
        teams = [self.team1, self.team2]
        self.storage.save_teams(teams)

        self.assertTrue(os.path.exists(self.storage_path))

    def test_save_teams_with_nested_directory(self):
        """Test that save_teams creates parent directories if needed."""
        nested_path = os.path.join(self.test_dir, "subdir", "teams.txt")
        storage = TeamDataStorage(nested_path)

        teams = [self.team1]
        storage.save_teams(teams)

        self.assertTrue(os.path.exists(nested_path))

        # Cleanup
        os.remove(nested_path)
        os.rmdir(os.path.dirname(nested_path))

    def test_save_and_load_teams(self):
        """Test saving and loading teams."""
        teams = [self.team1, self.team2, self.team3]
        self.storage.save_teams(teams)

        loaded_teams = self.storage.load_teams()

        self.assertEqual(len(loaded_teams), 3)
        self.assertEqual(loaded_teams[0].team_number, "1")
        self.assertEqual(loaded_teams[1].team_number, "2")
        self.assertEqual(loaded_teams[2].team_number, "3")

        # Verify first team members
        self.assertIsNotNone(loaded_teams[0].member1)
        self.assertEqual(loaded_teams[0].member1.student_id, "12345")
        self.assertEqual(loaded_teams[0].member1.name, "Juan Pérez")

    def test_load_teams_file_not_found(self):
        """Test that load_teams raises FileNotFoundError if file doesn't exist."""
        with self.assertRaises(FileNotFoundError):
            self.storage.load_teams()

    def test_save_empty_list(self):
        """Test saving an empty list of teams."""
        self.storage.save_teams([])

        loaded_teams = self.storage.load_teams()
        self.assertEqual(len(loaded_teams), 0)

    def test_iter_teams(self):
        """Test iterating over teams."""
        teams = [self.team1, self.team2, self.team3]
        self.storage.save_teams(teams)

        iterated_teams = list(self.storage.iter_teams())

        self.assertEqual(len(iterated_teams), 3)
        self.assertEqual(iterated_teams[0].team_number, "1")
        self.assertEqual(iterated_teams[1].team_number, "2")
        self.assertEqual(iterated_teams[2].team_number, "3")

    def test_iter_teams_file_not_found(self):
        """Test that iter_teams raises FileNotFoundError if file doesn't exist."""
        with self.assertRaises(FileNotFoundError):
            list(self.storage.iter_teams())

    def test_iter_teams_lazy_loading(self):
        """Test that iter_teams returns an iterator (lazy loading)."""
        teams = [self.team1, self.team2]
        self.storage.save_teams(teams)

        iterator = self.storage.iter_teams()

        # Iterator should be a generator, not a list
        self.assertTrue(hasattr(iterator, '__iter__'))
        self.assertTrue(hasattr(iterator, '__next__'))

    def test_find_team_by_number_found(self):
        """Test finding a team by number when it exists."""
        teams = [self.team1, self.team2, self.team3]
        self.storage.save_teams(teams)

        found_team = self.storage.find_team_by_number("2")

        self.assertIsNotNone(found_team)
        self.assertEqual(found_team.team_number, "2")
        self.assertEqual(found_team.member1.name, "Ana Martínez")

    def test_find_team_by_number_not_found(self):
        """Test finding a team by number when it doesn't exist."""
        teams = [self.team1, self.team2]
        self.storage.save_teams(teams)

        found_team = self.storage.find_team_by_number("999")

        self.assertIsNone(found_team)

    def test_find_team_by_number_file_not_found(self):
        """Test finding team when file doesn't exist returns None."""
        found_team = self.storage.find_team_by_number("1")

        self.assertIsNone(found_team)

    def test_exists_true(self):
        """Test exists returns True when file exists."""
        teams = [self.team1]
        self.storage.save_teams(teams)

        self.assertTrue(self.storage.exists())

    def test_exists_false(self):
        """Test exists returns False when file doesn't exist."""
        self.assertFalse(self.storage.exists())

    def test_save_overwrites_existing_file(self):
        """Test that save_teams overwrites existing file."""
        # Save initial teams
        initial_teams = [self.team1, self.team2]
        self.storage.save_teams(initial_teams)

        # Save new teams (should overwrite)
        new_teams = [self.team3]
        self.storage.save_teams(new_teams)

        # Load and verify only new teams exist
        loaded_teams = self.storage.load_teams()
        self.assertEqual(len(loaded_teams), 1)
        self.assertEqual(loaded_teams[0].team_number, "3")

    def test_save_teams_with_empty_members(self):
        """Test saving teams with varying numbers of members."""
        teams = [self.team1, self.team2, self.team3]
        self.storage.save_teams(teams)

        loaded_teams = self.storage.load_teams()

        # Team 1: 3 members
        self.assertEqual(len(loaded_teams[0].get_members()), 3)

        # Team 2: 2 members
        self.assertEqual(len(loaded_teams[1].get_members()), 2)

        # Team 3: 1 member
        self.assertEqual(len(loaded_teams[2].get_members()), 1)

    def test_file_format_consistency(self):
        """Test that saved file format is correct."""
        teams = [self.team1]
        self.storage.save_teams(teams)

        # Read raw file content
        with open(self.storage_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Verify format: team_number|member1|member2|member3
        expected = "1|12345, Juan Pérez|67890, María García|11223, Carlos López\n"
        self.assertEqual(content, expected)


if __name__ == '__main__':
    unittest.main()
