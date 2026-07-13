import os
import pytest
import sys

from data_fetchers.school_data.foothill import courses
from tests import data_verify
from tests.data_fetchers.schools.base_test import BaseSchoolTest

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) )

class TestFoothillCourses(BaseSchoolTest):
    @property
    def school_name(self):
        return "foothill"
    
    @property
    def test_type(self):
        return "courses"
    
    def test_update_courses_data_table(self):
        """Test getting courses from HTML"""
        soup = self.load_test_html_data("schedules_test_sample.html")
        
        def run_test():
            courses_data_table = set()
            courses.update_courses_data_table(soup, courses_data_table)
            return sorted(list(courses_data_table))
        
        # Run test with automatic result saving and data loading
        result = self.run_test_with_result_saving(run_test)
        
        # Additional verification
        assert isinstance(result, list)
        data_verify.verify_data_structure_courses_set(result)

if __name__ == "__main__":
    pytest.main([__file__]) 