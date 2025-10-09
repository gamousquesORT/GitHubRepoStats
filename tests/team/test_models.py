"""Unit tests for data models."""
import unittest
from src.team import Student, Team


class TestStudent(unittest.TestCase):
    """Test cases for Student class."""

    def test_from_csv_field_standard_format(self):
        """Test parsing student with standard format: ID, Name."""
        student = Student.from_csv_field("12345, Juan Pérez")
        self.assertIsNotNone(student)
        self.assertEqual(student.student_id, "12345")
        self.assertEqual(student.name, "Juan Pérez")

    def test_from_csv_field_reversed_format(self):
        """Test parsing student with name before ID."""
        student = Student.from_csv_field("María, García, 67890")
        self.assertIsNotNone(student)
        self.assertEqual(student.student_id, "67890")
        self.assertEqual(student.name, "María García")

    def test_from_csv_field_multiple_name_parts(self):
        """Test parsing student with multiple name parts."""
        student = Student.from_csv_field("11223, Carlos, Antonio, López, Martínez")
        self.assertIsNotNone(student)
        self.assertEqual(student.student_id, "11223")
        self.assertEqual(student.name, "Carlos Antonio López Martínez")

    def test_from_csv_field_id_in_middle(self):
        """Test parsing student with ID in the middle."""
        student = Student.from_csv_field("Ana, 44556, Martínez")
        self.assertIsNotNone(student)
        self.assertEqual(student.student_id, "44556")
        self.assertEqual(student.name, "Ana Martínez")

    def test_from_csv_field_empty_string(self):
        """Test parsing empty string returns None."""
        student = Student.from_csv_field("")
        self.assertIsNone(student)

    def test_from_csv_field_whitespace_only(self):
        """Test parsing whitespace only returns None."""
        student = Student.from_csv_field("   ")
        self.assertIsNone(student)

    def test_from_csv_field_no_id(self):
        """Test parsing field without numeric ID raises ValueError."""
        with self.assertRaises(ValueError):
            Student.from_csv_field("Juan Pérez")

    def test_from_csv_field_no_name(self):
        """Test parsing field with only ID raises ValueError."""
        with self.assertRaises(ValueError):
            Student.from_csv_field("12345")

    def test_str_representation(self):
        """Test string representation of student."""
        student = Student(student_id="12345", name="Juan Pérez")
        self.assertEqual(str(student), "12345, Juan Pérez")


class TestTeam(unittest.TestCase):
    """Test cases for Team class."""

    def test_team_creation_three_members(self):
        """Test creating team with three members."""
        s1 = Student("1", "Alice")
        s2 = Student("2", "Bob")
        s3 = Student("3", "Charlie")
        team = Team("1", s1, s2, s3)

        self.assertEqual(team.team_number, "1")
        self.assertEqual(len(team.get_members()), 3)

    def test_team_creation_two_members(self):
        """Test creating team with two members."""
        s1 = Student("1", "Alice")
        s2 = Student("2", "Bob")
        team = Team("2", s1, s2, None)

        self.assertEqual(team.team_number, "2")
        self.assertEqual(len(team.get_members()), 2)

    def test_team_creation_one_member(self):
        """Test creating team with one member."""
        s1 = Student("1", "Alice")
        team = Team("3", s1, None, None)

        self.assertEqual(team.team_number, "3")
        self.assertEqual(len(team.get_members()), 1)

    def test_to_file_format(self):
        """Test converting team to file format."""
        s1 = Student("1", "Alice")
        s2 = Student("2", "Bob")
        team = Team("1", s1, s2, None)

        result = team.to_file_format()
        self.assertEqual(result, "1|1, Alice|2, Bob|")

    def test_from_file_format(self):
        """Test parsing team from file format."""
        line = "1|12345, Juan Pérez|67890, María García|"
        team = Team.from_file_format(line)

        self.assertEqual(team.team_number, "1")
        self.assertIsNotNone(team.member1)
        self.assertIsNotNone(team.member2)
        self.assertIsNone(team.member3)
        self.assertEqual(team.member1.student_id, "12345")
        self.assertEqual(team.member2.name, "María García")


if __name__ == '__main__':
    unittest.main()
