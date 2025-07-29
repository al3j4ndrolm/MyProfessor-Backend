import os
import sys
import pytest
from time import sleep
from datetime import datetime, timedelta
from supabase import create_client

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.professors_db import save_one_entry, get_one_entry, should_update
from helpers.data import data_keys
from database import db_keys

def get_supabase_client():
    """Get Supabase client with environment variables"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        pytest.skip("SUPABASE_URL and SUPABASE_KEY environment variables are required")
    
    return create_client(url, key)

# Test data constants
TEST_SCHOOL = "Test University"
TEST_DEPARTMENT = "Computer Science"
TEST_PROFESSOR_NAME = "Dr. Test Professor"
TEST_PROFESSOR_EMAIL = "test.professor@testuniversity.edu"
TEST_UPDATE_PROFESSOR_NAME = "Dr. Update Test Professor"
TEST_UPDATE_PROFESSOR_EMAIL = "update.test.professor@testuniversity.edu"

def get_test_rmp_data():
    """Get mock RMP data for testing"""
    return {
        data_keys.PROFESSOR_RATING_KEY: 4.5,
        data_keys.PROFESSOR_DIFFICULTY_KEY: 3.2,
        data_keys.PROFESSOR_RECOMMEND_KEY: 95,
        data_keys.PROFESSOR_REVIEW_COUNT_KEY: 42,
        data_keys.PROFESSOR_SCORE_KEY: 4.3,
        data_keys.PROFESSOR_LINK_KEY: "https://www.ratemyprofessors.com/professor/test"
    }

class TestProfessorsDB:
    """Test class for professors_db functions"""
    supabase = get_supabase_client()
    
    def cleanup_test_data(self, supabase, test_school, test_department, test_professor_name, test_professor_email):
        """Clean up test data from the database"""
        try:
            # Delete test professor if it exists
            supabase.table("professors")\
                .delete()\
                .eq(db_keys.KEY_SCHOOL, test_school)\
                .execute()
        except Exception as e:
            # Ignore cleanup errors - test data might not exist
            pass
    
    def test_save_professor_with_timestamp(self):
        """Test that save_one_entry creates timestamps correctly"""
        
        # Test data
        test_rmp_data = get_test_rmp_data()
        
        try:
            # Clean up any existing test data first
            self.cleanup_test_data(self.supabase, TEST_SCHOOL, TEST_DEPARTMENT, TEST_PROFESSOR_NAME, TEST_PROFESSOR_EMAIL)
            
            # Save the test professor
            save_one_entry(self.supabase, TEST_SCHOOL, TEST_DEPARTMENT, TEST_PROFESSOR_NAME, TEST_PROFESSOR_EMAIL, test_rmp_data)
            
            # Retrieve the saved professor to check timestamps
            saved_professor = get_one_entry(self.supabase, TEST_SCHOOL, TEST_DEPARTMENT, TEST_PROFESSOR_NAME, TEST_PROFESSOR_EMAIL)
            
            # Assertions
            assert saved_professor is not None, "Professor should be saved successfully"
            assert db_keys.KEY_UPDATED_AT in saved_professor, "updated_at timestamp should be present"
            assert "id" in saved_professor, "id should be automatically generated"
            assert saved_professor[db_keys.KEY_UPDATED_AT] is not None, "updated_at should not be null"
            assert saved_professor["id"] is not None, "id should not be null"
            
            # Verify the data was saved correctly
            assert saved_professor[db_keys.KEY_PROFESSOR_NAME] == TEST_PROFESSOR_NAME
            assert saved_professor[db_keys.KEY_EMAIL] == TEST_PROFESSOR_EMAIL
            assert saved_professor[db_keys.KEY_SCHOOL] == TEST_SCHOOL
            assert saved_professor[db_keys.KEY_DEPARTMENT] == TEST_DEPARTMENT
            assert saved_professor[db_keys.KEY_RMP_RATING] == test_rmp_data[data_keys.PROFESSOR_RATING_KEY]
            assert saved_professor[db_keys.KEY_RMP_DIFFICULTY] == test_rmp_data[data_keys.PROFESSOR_DIFFICULTY_KEY]
            
        finally:
            # Clean up test data after test
            self.cleanup_test_data(self.supabase, TEST_SCHOOL, TEST_DEPARTMENT, TEST_PROFESSOR_NAME, TEST_PROFESSOR_EMAIL)
    
    def test_save_professor_update_existing(self):
        """Test that save_one_entry updates existing professor correctly"""
        
        # Test data
        test_rmp_data = get_test_rmp_data()
        
        try:
            # Clean up any existing test data first
            self.cleanup_test_data(self.supabase, TEST_SCHOOL, TEST_DEPARTMENT, TEST_UPDATE_PROFESSOR_NAME, TEST_UPDATE_PROFESSOR_EMAIL)
            
            # Save professor first time
            save_one_entry(self.supabase, TEST_SCHOOL, TEST_DEPARTMENT, TEST_UPDATE_PROFESSOR_NAME, TEST_UPDATE_PROFESSOR_EMAIL, test_rmp_data)
            first_save = get_one_entry(self.supabase, TEST_SCHOOL, TEST_DEPARTMENT, TEST_UPDATE_PROFESSOR_NAME, TEST_UPDATE_PROFESSOR_EMAIL)
            
            # Update with new data (save_one_entry always updates existing records)
            updated_rmp_data = test_rmp_data.copy()
            updated_rmp_data[data_keys.PROFESSOR_RATING_KEY] = 4.8
            updated_rmp_data[data_keys.PROFESSOR_DIFFICULTY_KEY] = 2.9
            
            save_one_entry(self.supabase, TEST_SCHOOL, TEST_DEPARTMENT, TEST_UPDATE_PROFESSOR_NAME, TEST_UPDATE_PROFESSOR_EMAIL, updated_rmp_data)
            second_save = get_one_entry(self.supabase, TEST_SCHOOL, TEST_DEPARTMENT, TEST_UPDATE_PROFESSOR_NAME, TEST_UPDATE_PROFESSOR_EMAIL)
            
            # Assertions
            assert first_save is not None, "First save should work"
            assert second_save is not None, "Second save should work"
            assert second_save[db_keys.KEY_RMP_RATING] == 4.8, "Rating should be updated"
            assert second_save[db_keys.KEY_RMP_DIFFICULTY] == 2.9, "Difficulty should be updated"
            assert second_save["id"] == first_save["id"], "ID should remain the same"
            assert second_save[db_keys.KEY_UPDATED_AT] != first_save[db_keys.KEY_UPDATED_AT], "updated_at should be different"
            
        finally:
            # Clean up test data after test
            self.cleanup_test_data(self.supabase, TEST_SCHOOL, TEST_DEPARTMENT, TEST_UPDATE_PROFESSOR_NAME, TEST_UPDATE_PROFESSOR_EMAIL)
    
    def test_should_update_function(self):
        """Test the should_update function that determines if data is more than 30 days old"""
        
        # Test with no updated_at field
        professor_no_timestamp = {}
        assert should_update(professor_no_timestamp) == True, "Should update when no updated_at field"
        
        # Test with null updated_at
        professor_null_timestamp = {db_keys.KEY_UPDATED_AT: None}
        assert should_update(professor_null_timestamp) == True, "Should update when updated_at is null"
        
        # Test with recent timestamp (less than 30 days)
        recent_timestamp = datetime.now() - timedelta(days=15)
        professor_recent = {db_keys.KEY_UPDATED_AT: recent_timestamp.isoformat()}
        assert should_update(professor_recent) == False, "Should not update when data is less than 30 days old"
        
        # Test with old timestamp (more than 30 days)
        old_timestamp = datetime.now() - timedelta(days=35)
        professor_old = {db_keys.KEY_UPDATED_AT: old_timestamp.isoformat()}
        assert should_update(professor_old) == True, "Should update when data is more than 30 days old"
    
    def test_get_one_entry_not_found(self):
        """Test that get_one_entry returns None for non-existent professor"""
        
        # Try to get a professor that doesn't exist
        result = get_one_entry(self.supabase, "NonExistentSchool", "NonExistentDept", "NonExistentProfessor", "nonexistent@test.edu")
        
        assert result is None, "Should return None for non-existent professor"

if __name__ == "__main__":
    pytest.main([__file__]) 