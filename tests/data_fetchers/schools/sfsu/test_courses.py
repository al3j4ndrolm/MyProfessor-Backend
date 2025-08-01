import os
import pytest
import sys

from data_fetchers.schools.sfsu import courses
from tests import data_verify
from tests.data_fetchers.schools.base_test import BaseSchoolTest

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) )

class TestSFSUCourses(BaseSchoolTest):
    @property
    def school_name(self):
        return "sfsu"
    
    @property
    def test_type(self):
        return "courses"
    
    def test_update_courses_set_per_term(self):
        """Test getting courses for term 2257"""
        session_data = self.load_test_session_data()
        courses_set = set()
        
        def run_test():
            result = courses.update_courses_set_per_term(session_data, courses_set)
            return sorted(list(result))
        
        # Run test with automatic result saving and data loading
        result = self.run_test_with_result_saving(run_test)
        
        # Additional verification
        data_verify.verify_data_structure_courses_set(result)

if __name__ == "__main__":
    pytest.main([__file__])
