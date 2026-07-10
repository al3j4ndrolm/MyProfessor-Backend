import os
import sys
import pytest
from unittest.mock import Mock

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.courses_db import save, get
from database import db_keys

TEST_SCHOOL = "Test University"
TEST_COURSES_DATA = {"Computer Science": ["CS101", "CS102"]}

class TestCoursesDB:
    """Test class for courses_db functions"""

    def test_save_upserts_courses_data(self):
        """Test that save upserts course data keyed on school"""

        mock_supabase = Mock()
        mock_table = Mock()
        mock_upsert = Mock()

        mock_supabase.table.return_value = mock_table
        mock_table.upsert.return_value = mock_upsert

        save(mock_supabase, TEST_COURSES_DATA, TEST_SCHOOL)

        mock_supabase.table.assert_called_once_with("courses")
        mock_table.upsert.assert_called_once_with(
            {db_keys.COURSES_KEY_SCHOOL: TEST_SCHOOL, db_keys.COURSES_KEY_DATA: {"Computer Science": ["CS101", "CS102"]}},
            on_conflict=db_keys.COURSES_KEY_SCHOOL,
        )
        mock_upsert.execute.assert_called_once()

    def test_get_returns_empty_dict_when_not_found(self):
        """Test that get returns an empty dict when no course data exists for a school"""

        mock_supabase = Mock()
        mock_table = Mock()
        mock_select = Mock()
        mock_eq = Mock()
        mock_response = Mock()
        mock_response.data = []

        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.eq.return_value = mock_eq
        mock_eq.execute.return_value = mock_response

        result = get(mock_supabase, TEST_SCHOOL)

        assert result == {}

    def test_get_returns_data_when_found(self):
        """Test that get returns the stored data field when a match exists"""

        mock_supabase = Mock()
        mock_table = Mock()
        mock_select = Mock()
        mock_eq = Mock()
        mock_response = Mock()
        mock_response.data = [{db_keys.COURSES_KEY_DATA: TEST_COURSES_DATA}]

        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.eq.return_value = mock_eq
        mock_eq.execute.return_value = mock_response

        result = get(mock_supabase, TEST_SCHOOL)

        mock_supabase.table.assert_called_once_with("courses")
        mock_table.select.assert_called_once_with("*")
        mock_select.eq.assert_called_once_with(db_keys.COURSES_KEY_SCHOOL, TEST_SCHOOL)
        assert result == TEST_COURSES_DATA

if __name__ == "__main__":
    pytest.main([__file__])
