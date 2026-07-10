import os
import sys
import pytest
from unittest.mock import Mock

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.reports_db import save, save_error
from database import db_keys

TEST_BUILD = "1.2.3"
TEST_PLATFORM = "ios"
TEST_DATA = {"message": "something went wrong"}
TEST_VERSION = "1.0.0"
TEST_CRITICAL = True
TEST_DETAILS = "stack trace details"

class TestReportsDB:
    """Test class for reports_db functions"""

    def test_save_inserts_report_row(self):
        """Test that save inserts a report row built from build, platform, and data"""

        mock_supabase = Mock()
        mock_table = Mock()
        mock_insert = Mock()

        mock_supabase.table.return_value = mock_table
        mock_table.insert.return_value = mock_insert

        save(mock_supabase, TEST_BUILD, TEST_PLATFORM, TEST_DATA)

        mock_supabase.table.assert_called_once_with("reports")
        mock_table.insert.assert_called_once_with({
            db_keys.REPORTS_KEY_VERSION: None,
            db_keys.REPORTS_KEY_CRITICAL: False,
            db_keys.REPORTS_KEY_DETAILS: str(TEST_DATA),
            db_keys.REPORTS_KEY_PLATFORM: TEST_PLATFORM,
            db_keys.REPORTS_KEY_BUILD: TEST_BUILD,
            db_keys.REPORTS_KEY_IS_ERROR: False,
        })
        mock_insert.execute.assert_called_once()

    def test_save_error_inserts_error_report_row(self):
        """Test that save_error inserts a report row with is_error set to True"""

        mock_supabase = Mock()
        mock_table = Mock()
        mock_insert = Mock()

        mock_supabase.table.return_value = mock_table
        mock_table.insert.return_value = mock_insert

        save_error(mock_supabase, TEST_VERSION, TEST_CRITICAL, TEST_DETAILS, TEST_PLATFORM, TEST_BUILD)

        mock_supabase.table.assert_called_once_with("reports")
        mock_table.insert.assert_called_once_with({
            db_keys.REPORTS_KEY_VERSION: TEST_VERSION,
            db_keys.REPORTS_KEY_CRITICAL: TEST_CRITICAL,
            db_keys.REPORTS_KEY_DETAILS: TEST_DETAILS,
            db_keys.REPORTS_KEY_PLATFORM: TEST_PLATFORM,
            db_keys.REPORTS_KEY_BUILD: TEST_BUILD,
            db_keys.REPORTS_KEY_IS_ERROR: True,
        })
        mock_insert.execute.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__])
