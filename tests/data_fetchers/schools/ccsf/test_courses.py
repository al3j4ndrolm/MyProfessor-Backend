import os
import pytest
import sys

from data_fetchers.schools.ccsf import courses
from tests.data_fetchers.schools.base_test import BaseSchoolTest

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) )

class TestCCSFCourses(BaseSchoolTest):
    @property
    def school_name(self):
        return "ccsf"
    
    @property
    def test_type(self):
        return "courses"
    
    def test_get_courses_per_department(self):
        """Test getting courses from HTML"""
        soup = self.load_test_html_data("courses_test_sample.html")
        
        def run_test():
            result = courses.get_courses_per_department(soup, "")  # Empty string to get all courses
            return sorted(list(result))
        
        # Run test with automatic result saving and data loading
        result = self.run_test_with_result_saving(run_test)
        
        # Additional verification
        assert isinstance(result, list)

if __name__ == "__main__":
    pytest.main([__file__]) 