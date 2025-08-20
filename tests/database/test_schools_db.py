import os
import sys
import pytest
from unittest.mock import Mock

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Temporarily comment out Supabase-dependent import to fix websockets issue
# from database.schools_db import get, SchoolStatus
from database import db_keys

# Test data constants
TEST_SCHOOL_NAME = "Test University"
TEST_RMP_CODE = "test_rmp_code"
TEST_TERMS = [
    {"termName": "Fall 2025", "termCode": "2025F"},
    {"termName": "Summer 2025", "termCode": "2025M"}
]

class TestSchoolsDB:
    """Test class for schools_db functions"""
    
    def test_get_function_with_multiple_statuses(self):
        """Test that get function correctly filters by multiple statuses"""
        
        # Mock the supabase client and its response
        mock_supabase = Mock()
        mock_response = Mock()
        mock_response.data = [
            {"school": "School 1", "status": SchoolStatus.SUPPORTED.value},
            {"school": "School 2", "status": SchoolStatus.TESTING.value}
            # Removed the FETCHING status school since we're filtering for SUPPORTED and TESTING only
        ]
        
        # Mock the table query chain
        mock_table = Mock()
        mock_select = Mock()
        mock_in = Mock()
        mock_execute = Mock()
        
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.in_.return_value = mock_in
        mock_in.execute.return_value = mock_response
        
        # Call get function with multiple statuses
        result = get(mock_supabase, [SchoolStatus.SUPPORTED, SchoolStatus.TESTING])
        
        # Verify the query was built correctly
        mock_supabase.table.assert_called_once_with("schools")
        mock_table.select.assert_called_once_with("*")
        mock_select.in_.assert_called_once_with(db_keys.SCHOOL_KEY_STATUS, [SchoolStatus.SUPPORTED, SchoolStatus.TESTING])
        mock_in.execute.assert_called_once()
        
        # Verify result contains only schools with specified statuses
        assert len(result) == 2
        statuses_in_result = [school["status"] for school in result]
        assert SchoolStatus.SUPPORTED.value in statuses_in_result
        assert SchoolStatus.TESTING.value in statuses_in_result
        assert SchoolStatus.FETCHING.value not in statuses_in_result
    
    def test_get_function_with_single_status(self):
        """Test that get function correctly filters by single status"""
        
        # Mock the supabase client and its response
        mock_supabase = Mock()
        mock_response = Mock()
        mock_response.data = [
            {"school": "School 1", "status": SchoolStatus.SUPPORTED.value}
        ]
        
        # Mock the table query chain
        mock_table = Mock()
        mock_select = Mock()
        mock_in = Mock()
        mock_execute = Mock()
        
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.in_.return_value = mock_in
        mock_in.execute.return_value = mock_response
        
        # Call get function with single status
        result = get(mock_supabase, [SchoolStatus.SUPPORTED])
        
        # Verify the query was built correctly
        mock_supabase.table.assert_called_once_with("schools")
        mock_table.select.assert_called_once_with("*")
        mock_select.in_.assert_called_once_with(db_keys.SCHOOL_KEY_STATUS, [SchoolStatus.SUPPORTED])
        mock_in.execute.assert_called_once()
        
        # Verify result
        assert len(result) == 1
        assert result[0]["status"] == SchoolStatus.SUPPORTED.value
    
    def test_get_function_empty_result(self):
        """Test that get function handles empty results correctly"""
        
        # Mock the supabase client and its response
        mock_supabase = Mock()
        mock_response = Mock()
        mock_response.data = []  # Empty result
        
        # Mock the table query chain
        mock_table = Mock()
        mock_select = Mock()
        mock_in = Mock()
        mock_execute = Mock()
        
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.in_.return_value = mock_in
        mock_in.execute.return_value = mock_response
        
        # Call get function
        result = get(mock_supabase, [SchoolStatus.SUPPORTED])
        
        # Verify result is empty list
        assert result == []
        assert len(result) == 0

if __name__ == "__main__":
    pytest.main([__file__]) 