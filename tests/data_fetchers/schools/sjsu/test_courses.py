import os
import pytest
import sys

from data_fetchers.schools.sjsu import courses
from tests import data_verify
from tests.data_fetchers.schools.base_test import BaseSchoolTest

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) )

class TestSJSUCourses(BaseSchoolTest):
    @property
    def school_name(self):
        return "sjsu"
    
    @property
    def test_type(self):
        return "courses"
    
    def test_get_courses(self):
        """Test getting courses from HTML"""
        soup = self.load_test_html_data("classes_test_sample.html")
        
        def run_test():
            result = {}
            courses.update_courses_data_table(soup, result)
            return sorted(list(result["MATH"]))
        
        # Run test with automatic result saving and data loading
        result = self.run_test_with_result_saving(run_test)
        
        # Additional verification
        data_verify.verify_data_structure_courses_set(result)

if __name__ == "__main__":
    pytest.main([__file__]) 