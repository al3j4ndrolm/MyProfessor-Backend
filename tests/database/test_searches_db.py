import os
import sys
import pytest
from unittest.mock import Mock

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.searches_db import save
from database import db_keys

TEST_SCHOOL = "Test University"
TEST_TERM = "2025F"
TEST_DEPARTMENT = "Computer Science"

class TestSearchesDB:
    """Test class for searches_db functions"""

    def test_save_inserts_search_row(self):
        """Test that save inserts a search row with school, term, and department"""

        mock_supabase = Mock()
        mock_table = Mock()
        mock_insert = Mock()

        mock_supabase.table.return_value = mock_table
        mock_table.insert.return_value = mock_insert

        save(mock_supabase, TEST_SCHOOL, TEST_TERM, TEST_DEPARTMENT)

        mock_supabase.table.assert_called_once_with("searches")
        mock_table.insert.assert_called_once_with({
            db_keys.SEARCHES_KEY_SCHOOL: TEST_SCHOOL,
            db_keys.SEARCHES_KEY_TERM: TEST_TERM,
            db_keys.SEARCHES_KEY_DEPARTMENT: TEST_DEPARTMENT,
        })
        mock_insert.execute.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__])
