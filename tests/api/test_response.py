import os
import sys
import pytest
from unittest.mock import Mock, patch

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from api.response import response_start
from database.schools_db import SchoolStatus
from database import db_keys
from api import configs

class TestResponse:
    """Test class for response.py functions"""
    
    def test_response_start_dev_build(self):
        """Test response_start with dev build type returns SUPPORTED and TESTING schools"""
        
        # Mock the supabase client
        mock_supabase = Mock()
        
        # Mock data
        mock_schools_data = [
            {
                db_keys.SCHOOL_KEY_SCHOOL_NAME: "Test School 1",
                db_keys.SCHOOL_KEY_TERMS: [{"termName": "Fall 2025", "termCode": "2025F"}],
                db_keys.SCHOOL_KEY_NOTIFICATION: "Test notification",
                db_keys.SCHOOL_KEY_STATUS: SchoolStatus.SUPPORTED.value,
                db_keys.KEY_UPDATED_AT: "2025-01-01T00:00:00Z",
                db_keys.SCHOOL_KEY_COURSES_UPDATED_AT: "2025-01-01T00:00:00Z",
                db_keys.SCHOOL_KEY_FEATURES: {"feature1": True, "feature2": False}
            },
            {
                db_keys.SCHOOL_KEY_SCHOOL_NAME: "Test School 2",
                db_keys.SCHOOL_KEY_TERMS: [{"termName": "Spring 2025", "termCode": "2025S"}],
                db_keys.SCHOOL_KEY_NOTIFICATION: "",
                db_keys.SCHOOL_KEY_STATUS: SchoolStatus.TESTING.value,
                db_keys.KEY_UPDATED_AT: "2025-01-02T00:00:00Z",
                db_keys.SCHOOL_KEY_COURSES_UPDATED_AT: "2025-01-01T00:00:00Z",
                db_keys.SCHOOL_KEY_FEATURES: {"feature1": False, "feature2": False}
            }
        ]
        
        mock_broadcasts_data = [
            {
                db_keys.BROADCAST_KEY_ID: "broadcast1",
                db_keys.BROADCAST_KEY_TEXT: "Test broadcast",
                db_keys.BROADCAST_KEY_MIN_VERSION: "1.0.0"
            }
        ]
        
        # Mock the database calls
        with patch('api.response.schools_db.get') as mock_get_schools, \
             patch('api.response.broadcasts_db.get_active') as mock_get_broadcasts:
            
            mock_get_schools.return_value = mock_schools_data
            mock_get_broadcasts.return_value = mock_broadcasts_data
            
            # Call response_start with dev build type
            result = response_start(mock_supabase, {"build_type": "dev"}, {})
            
            # Verify schools_db.get was called with correct statuses
            mock_get_schools.assert_called_once_with(mock_supabase, [SchoolStatus.SUPPORTED, SchoolStatus.TESTING])
            
            # Verify broadcasts_db.get_active was called
            mock_get_broadcasts.assert_called_once_with(mock_supabase)
            
            # Verify result structure
            assert configs.SCHOOLS_KEY_SCHOOL_LIST in result
            assert configs.SCHOOLS_KEY_BROADCASTS in result
            
            # Verify school list
            school_list = result[configs.SCHOOLS_KEY_SCHOOL_LIST]
            assert len(school_list) == 2
            assert school_list[0][configs.SCHOOL_NAME] == "Test School 1"
            assert school_list[1][configs.SCHOOL_NAME] == "Test School 2"
            
            # Verify broadcast list
            broadcast_list = result[configs.SCHOOLS_KEY_BROADCASTS]
            assert len(broadcast_list) == 1
            assert broadcast_list[0][configs.BROADCAST_ID] == "broadcast1"
    
    def test_response_start_release_build(self):
        """Test response_start with release build type returns only SUPPORTED schools"""
        
        # Mock the supabase client
        mock_supabase = Mock()
        
        # Mock data
        mock_schools_data = [
            {
                db_keys.SCHOOL_KEY_SCHOOL_NAME: "Production School",
                db_keys.SCHOOL_KEY_TERMS: [{"termName": "Fall 2025", "termCode": "2025F"}],
                db_keys.SCHOOL_KEY_NOTIFICATION: "",
                db_keys.SCHOOL_KEY_STATUS: SchoolStatus.SUPPORTED.value,
                db_keys.KEY_UPDATED_AT: "2025-01-01T00:00:00Z",
                db_keys.SCHOOL_KEY_COURSES_UPDATED_AT: "2025-01-01T00:00:00Z",
                db_keys.SCHOOL_KEY_FEATURES: {"feature1": False, "feature2": False}
            }
        ]

        mock_broadcasts_data = []

        # Mock the database calls
        with patch('api.response.schools_db.get') as mock_get_schools, \
             patch('api.response.broadcasts_db.get_active') as mock_get_broadcasts:

            mock_get_schools.return_value = mock_schools_data
            mock_get_broadcasts.return_value = mock_broadcasts_data

            # Call response_start with prod build type
            result = response_start(mock_supabase, {"build_type": "release"}, {})
            
            # Verify schools_db.get was called with only SUPPORTED status
            mock_get_schools.assert_called_once_with(mock_supabase, [SchoolStatus.SUPPORTED])
            
            # Verify result
            school_list = result[configs.SCHOOLS_KEY_SCHOOL_LIST]
            assert len(school_list) == 1
            assert school_list[0][configs.SCHOOL_NAME] == "Production School"
            
            broadcast_list = result[configs.SCHOOLS_KEY_BROADCASTS]
            assert len(broadcast_list) == 0
    
    def test_response_start_other_build_type(self):
        """Test response_start with other build type returns empty school list"""
        
        # Mock the supabase client
        mock_supabase = Mock()
        
        # Mock the database calls
        with patch('api.response.schools_db.get') as mock_get_schools, \
             patch('api.response.broadcasts_db.get_active') as mock_get_broadcasts:
            
            mock_get_schools.return_value = []
            mock_get_broadcasts.return_value = []
            
            # Call response_start with other build type
            result = response_start(mock_supabase, {"build_type": "staging"}, {})
            
            # Verify schools_db.get was called with empty list
            mock_get_schools.assert_called_once_with(mock_supabase, [])
            
            # Verify result
            school_list = result[configs.SCHOOLS_KEY_SCHOOL_LIST]
            assert len(school_list) == 0
    
    def test_response_start_no_build_type(self):
        """Test response_start with no build type returns empty school list"""
        
        # Mock the supabase client
        mock_supabase = Mock()
        
        # Mock the database calls
        with patch('api.response.schools_db.get') as mock_get_schools, \
             patch('api.response.broadcasts_db.get_active') as mock_get_broadcasts:
            
            mock_get_schools.return_value = []
            mock_get_broadcasts.return_value = []
            
            # Call response_start with no build type
            result = response_start(mock_supabase, {}, {})
            
            # Verify schools_db.get was called with empty list
            mock_get_schools.assert_called_once_with(mock_supabase, [])
            
            # Verify result
            school_list = result[configs.SCHOOLS_KEY_SCHOOL_LIST]
            assert len(school_list) == 0
    
    def test_create_school_format(self):
        """Test that _create_school formats school data correctly"""
        
        # Mock the supabase client
        mock_supabase = Mock()
        
        # Test data
        mock_schools_data = [
            {
                db_keys.SCHOOL_KEY_SCHOOL_NAME: "Test School",
                db_keys.SCHOOL_KEY_TERMS: [{"termName": "Fall 2025", "termCode": "2025F"}],
                db_keys.SCHOOL_KEY_NOTIFICATION: "Test notification",
                db_keys.SCHOOL_KEY_STATUS: SchoolStatus.SUPPORTED.value,
                db_keys.KEY_UPDATED_AT: "2025-01-01T00:00:00Z",
                db_keys.SCHOOL_KEY_COURSES_UPDATED_AT: "2025-01-01T00:00:00Z",
                db_keys.SCHOOL_KEY_FEATURES: {"feature1": True, "feature2": False}
            }
        ]

        mock_broadcasts_data = []

        # Mock the database calls
        with patch('api.response.schools_db.get') as mock_get_schools, \
             patch('api.response.broadcasts_db.get_active') as mock_get_broadcasts:

            mock_get_schools.return_value = mock_schools_data
            mock_get_broadcasts.return_value = mock_broadcasts_data

            # Call response_start
            result = response_start(mock_supabase, {"build_type": "dev"}, {})

            # Verify school format
            school = result[configs.SCHOOLS_KEY_SCHOOL_LIST][0]
            assert school[configs.SCHOOL_NAME] == "Test School"
            assert school[configs.SCHOOL_TERMS] == [{"termName": "Fall 2025", "termCode": "2025F"}]
            assert school[configs.SCHOOL_NOTIFICATION] == {"text": "Test notification"}
            assert school[configs.SCHOOL_STATUS] == SchoolStatus.SUPPORTED.value
            assert school[configs.SCHOOL_UPDATED_AT] == "2025-01-01T00:00:00Z"
            assert "schoolRmpCode" not in school  # New format doesn't include RMP code
    
    def test_create_broadcast_format(self):
        """Test that _create_broadcast formats broadcast data correctly"""
        
        # Mock the supabase client
        mock_supabase = Mock()
        
        # Test data
        mock_schools_data = []
        mock_broadcasts_data = [
            {
                db_keys.BROADCAST_KEY_ID: "broadcast1",
                db_keys.BROADCAST_KEY_TEXT: "Test broadcast message",
                db_keys.BROADCAST_KEY_MIN_VERSION: "2.0.0"
            }
        ]
        
        # Mock the database calls
        with patch('api.response.schools_db.get') as mock_get_schools, \
             patch('api.response.broadcasts_db.get_active') as mock_get_broadcasts:
            
            mock_get_schools.return_value = mock_schools_data
            mock_get_broadcasts.return_value = mock_broadcasts_data
            
            # Call response_start
            result = response_start(mock_supabase, {"build_type": "dev"}, {})
            
            # Verify broadcast format
            broadcast = result[configs.SCHOOLS_KEY_BROADCASTS][0]
            assert broadcast[configs.BROADCAST_ID] == "broadcast1"
            assert broadcast[configs.BROADCAST_TEXT] == "Test broadcast message"
            assert broadcast[configs.BROADCAST_MIN_VERSION] == "2.0.0"
            assert "needUpdate" not in broadcast  # New format doesn't include needUpdate field

if __name__ == "__main__":
    pytest.main([__file__]) 