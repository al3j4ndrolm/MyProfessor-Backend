import os
import sys
import pytest
from unittest.mock import Mock

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.classes_db import save_one_entry, get_one_entry, select_query, select_all_for_school
from database import db_keys

TEST_SCHOOL = "Test University"
TEST_DEPARTMENT = "Computer Science"
TEST_TERM = "2025F"
TEST_DATA = {"CS101": ["Section 1", "Section 2"]}

def build_select_chain(mock_supabase, response_data):
    mock_table = Mock()
    mock_select = Mock()
    mock_eq_school = Mock()
    mock_eq_term = Mock()
    mock_eq_department = Mock()
    mock_response = Mock()
    mock_response.data = response_data

    mock_supabase.table.return_value = mock_table
    mock_table.select.return_value = mock_select
    mock_select.eq.return_value = mock_eq_school
    mock_eq_school.eq.return_value = mock_eq_term
    mock_eq_term.eq.return_value = mock_eq_department
    mock_eq_department.execute.return_value = mock_response

    return mock_table, mock_select, mock_eq_department

class TestClassesDB:
    """Test class for classes_db functions"""

    def test_select_query_builds_correct_filters(self):
        """Test that select_query filters by school, term, and department"""

        mock_supabase = Mock()
        mock_table, mock_select, mock_eq_department = build_select_chain(mock_supabase, [])

        select_query(mock_supabase, TEST_SCHOOL, TEST_TERM, TEST_DEPARTMENT)

        mock_supabase.table.assert_called_once_with("classes")
        mock_table.select.assert_called_once_with("*")
        mock_select.eq.assert_called_once_with(db_keys.CLASSES_KEY_SCHOOL, TEST_SCHOOL)
        mock_eq_department.execute.assert_called_once()

    def test_get_one_entry_returns_empty_dict_when_not_found(self):
        """Test that get_one_entry returns an empty dict when no matching classes exist"""

        mock_supabase = Mock()
        build_select_chain(mock_supabase, [])

        result = get_one_entry(mock_supabase, TEST_SCHOOL, TEST_TERM, TEST_DEPARTMENT)

        assert result == {}

    def test_get_one_entry_returns_data_when_found(self):
        """Test that get_one_entry returns the stored data field when a match exists"""

        mock_supabase = Mock()
        build_select_chain(mock_supabase, [{db_keys.CLASSES_KEY_DATA: TEST_DATA}])

        result = get_one_entry(mock_supabase, TEST_SCHOOL, TEST_TERM, TEST_DEPARTMENT)

        assert result == TEST_DATA

    def test_save_one_entry_inserts_when_no_existing_entry(self):
        """Test that save_one_entry inserts a new row when none exists yet"""

        mock_supabase = Mock()
        build_select_chain(mock_supabase, [])

        mock_insert = Mock()
        mock_supabase.table.return_value.insert.return_value = mock_insert

        save_one_entry(mock_supabase, TEST_DATA, TEST_SCHOOL, TEST_TERM, TEST_DEPARTMENT)

        mock_supabase.table.return_value.insert.assert_called_once_with({
            db_keys.CLASSES_KEY_SCHOOL: TEST_SCHOOL,
            db_keys.CLASSES_KEY_DEPARTMENT: TEST_DEPARTMENT,
            db_keys.CLASSES_KEY_TERM: TEST_TERM,
            db_keys.CLASSES_KEY_DATA: TEST_DATA,
        })
        mock_insert.execute.assert_called_once()

    def test_save_one_entry_updates_when_data_changed(self):
        """Test that save_one_entry updates the row when the stored data differs"""

        mock_supabase = Mock()
        build_select_chain(mock_supabase, [{db_keys.CLASSES_KEY_DATA: {"old": "data"}}])

        mock_update = Mock()
        mock_eq_1 = Mock()
        mock_eq_2 = Mock()
        mock_eq_3 = Mock()
        mock_supabase.table.return_value.update.return_value = mock_update
        mock_update.eq.return_value = mock_eq_1
        mock_eq_1.eq.return_value = mock_eq_2
        mock_eq_2.eq.return_value = mock_eq_3

        save_one_entry(mock_supabase, TEST_DATA, TEST_SCHOOL, TEST_TERM, TEST_DEPARTMENT)

        mock_supabase.table.return_value.update.assert_called_once_with({db_keys.CLASSES_KEY_DATA: TEST_DATA})
        mock_eq_3.execute.assert_called_once()

    def test_save_one_entry_noop_when_data_unchanged(self):
        """Test that save_one_entry does nothing when the stored data already matches"""

        mock_supabase = Mock()
        build_select_chain(mock_supabase, [{db_keys.CLASSES_KEY_DATA: TEST_DATA}])

        save_one_entry(mock_supabase, TEST_DATA, TEST_SCHOOL, TEST_TERM, TEST_DEPARTMENT)

        mock_supabase.table.return_value.insert.assert_not_called()
        mock_supabase.table.return_value.update.assert_not_called()

    def test_select_all_for_school_filters_by_school_only(self):
        """Test that select_all_for_school only filters by school"""

        mock_supabase = Mock()
        mock_table = Mock()
        mock_select = Mock()
        mock_eq = Mock()
        mock_response = Mock()
        mock_response.data = [{db_keys.CLASSES_KEY_DATA: TEST_DATA}]

        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.eq.return_value = mock_eq
        mock_eq.execute.return_value = mock_response

        result = select_all_for_school(mock_supabase, TEST_SCHOOL)

        mock_supabase.table.assert_called_once_with("classes")
        mock_select.eq.assert_called_once_with(db_keys.CLASSES_KEY_SCHOOL, TEST_SCHOOL)
        assert result == mock_response

if __name__ == "__main__":
    pytest.main([__file__])
