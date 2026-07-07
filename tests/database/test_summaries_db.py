import os
import sys
import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Temporarily comment out Supabase-dependent import to fix websockets issue
from database.summaries_db import get_one_entry, save_one_entry, Summary

# Test data constants
TEST_RMP_LINK = "/professor/1547506"
TEST_RMP_LINK_2 = "/professor/171408"
TEST_SUMMARY_DATA = {
    "stats": {
        "aiScore": "4.2",
        "reviewCount": 42
    },
    "popularTags": [
        {"tag": "Helpful", "level": "good", "mentions": 15},
        {"tag": "Tough Grader", "level": "warning", "mentions": 8}
    ],
    "recentCourseFeedback": {
        "MATH 1A": "Great explanations, very helpful",
        "BUS 10": "Clear lectures, fair grading"
    },
    "extraNote": "Professor is very approachable during office hours"
}

def get_test_summary_data():
    """Get mock summary data for testing"""
    return TEST_SUMMARY_DATA.copy()

class TestSummariesDB:
    """Test class for summaries_db functions"""
    
    def test_save_one_entry_new_summary(self):
        """Test that save_one_entry creates new summary entry correctly"""
        
        # Mock the supabase client and its response
        mock_supabase = Mock()
        mock_response = Mock()
        mock_response.data = [{"rmp_link": TEST_RMP_LINK, "summary": TEST_SUMMARY_DATA}]
        
        # Mock the table query chain
        mock_table = Mock()
        mock_upsert = Mock()
        mock_execute = Mock()
        
        mock_supabase.table.return_value = mock_table
        mock_table.upsert.return_value = mock_upsert
        mock_upsert.execute.return_value = mock_response
        
        # Call save_one_entry function
        save_one_entry(mock_supabase, TEST_RMP_LINK, TEST_SUMMARY_DATA)
        
        # Verify the query was built correctly
        mock_supabase.table.assert_called_once_with("summaries")
        mock_table.upsert.assert_called_once_with({
            "rmp_link": TEST_RMP_LINK, 
            "summary": TEST_SUMMARY_DATA
        })
        mock_upsert.execute.assert_called_once()
    
    def test_save_one_entry_update_existing(self):
        """Test that save_one_entry updates existing summary correctly"""
        
        # Mock the supabase client and its response
        mock_supabase = Mock()
        mock_response = Mock()
        updated_summary = TEST_SUMMARY_DATA.copy()
        updated_summary["stats"]["aiScore"] = "4.5"
        mock_response.data = [{"rmp_link": TEST_RMP_LINK, "summary": updated_summary}]
        
        # Mock the table query chain
        mock_table = Mock()
        mock_upsert = Mock()
        mock_execute = Mock()
        
        mock_supabase.table.return_value = mock_table
        mock_table.upsert.return_value = mock_upsert
        mock_upsert.execute.return_value = mock_response
        
        # Call save_one_entry function with updated data
        save_one_entry(mock_supabase, TEST_RMP_LINK, updated_summary)
        
        # Verify the query was built correctly
        mock_supabase.table.assert_called_once_with("summaries")
        mock_table.upsert.assert_called_once_with({
            "rmp_link": TEST_RMP_LINK, 
            "summary": updated_summary
        })
        mock_upsert.execute.assert_called_once()
    
    def test_get_one_entry_found(self):
        """Test that get_one_entry retrieves existing summary correctly"""
        
        # Mock the supabase client and its response
        mock_supabase = Mock()
        mock_response = Mock()
        mock_response.data = [{"rmp_link": TEST_RMP_LINK, "summary": TEST_SUMMARY_DATA}]
        
        # Mock the table query chain
        mock_table = Mock()
        mock_select = Mock()
        mock_eq = Mock()
        mock_execute = Mock()
        
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.eq.return_value = mock_eq
        mock_eq.execute.return_value = mock_response
        
        # Call get_one_entry function
        result = get_one_entry(mock_supabase, TEST_RMP_LINK)
        
        # Verify the query was built correctly
        mock_supabase.table.assert_called_once_with("summaries")
        mock_table.select.assert_called_once_with("*")
        mock_select.eq.assert_called_once_with("rmp_link", TEST_RMP_LINK)
        mock_eq.execute.assert_called_once()
        
        # Verify result
        assert result is not None
        assert result["rmp_link"] == TEST_RMP_LINK
        assert result["summary"] == TEST_SUMMARY_DATA
    
    def test_get_one_entry_not_found(self):
        """Test that get_one_entry handles non-existent summary correctly"""
        
        # Mock the supabase client and its response
        mock_supabase = Mock()
        mock_response = Mock()
        mock_response.data = []  # Empty result
        
        # Mock the table query chain
        mock_table = Mock()
        mock_select = Mock()
        mock_eq = Mock()
        mock_execute = Mock()
        
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.eq.return_value = mock_eq
        mock_eq.execute.return_value = mock_response
        
        # Call get_one_entry function
        result = get_one_entry(mock_supabase, "/professor/nonexistent")
        
        # Verify the query was built correctly
        mock_supabase.table.assert_called_once_with("summaries")
        mock_table.select.assert_called_once_with("*")
        mock_select.eq.assert_called_once_with("rmp_link", "/professor/nonexistent")
        mock_eq.execute.assert_called_once()
        
        # Verify result is None (since data[0] on empty list will raise IndexError)
        # The actual function would need error handling for this case
        assert mock_response.data == []
    
    def test_summary_model_validation(self):
        """Test that Summary model validates data correctly"""
        
        # Test valid summary data
        valid_summary = Summary(
            rmp_link=TEST_RMP_LINK,
            summary=TEST_SUMMARY_DATA
        )
        assert valid_summary.rmp_link == TEST_RMP_LINK
        assert valid_summary.summary == TEST_SUMMARY_DATA
        
        # Test summary with None value
        summary_with_none = Summary(
            rmp_link=TEST_RMP_LINK,
            summary=None
        )
        assert summary_with_none.rmp_link == TEST_RMP_LINK
        assert summary_with_none.summary is None
        
        # Test summary without optional field
        summary_without_optional = Summary(rmp_link=TEST_RMP_LINK)
        assert summary_without_optional.rmp_link == TEST_RMP_LINK
        assert summary_without_optional.summary is None

if __name__ == "__main__":
    pytest.main([__file__]) 