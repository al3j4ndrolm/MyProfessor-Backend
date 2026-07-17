import os
import pytest
import sys

from data_fetchers.school_data.schools.sjsu import schedules
from tests import data_verify
from tests.data_fetchers.schools.base_test import BaseSchoolTest

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) )

class TestSJSUSchedules(BaseSchoolTest):
    @property
    def school_name(self):
        return "sjsu"
    
    @property
    def test_type(self):
        return "classes"
    
    def test_get_schedules(self):
        """Test getting schedules for ART department"""
        soup = self.load_test_html_data("classes_test_sample.html")
        departments = {"ART"}
        
        def run_test():
            result = schedules.get_classes_per_department(soup, departments)
            return result
        
        # Run test with automatic result saving and data loading
        result = self.run_test_with_result_saving(run_test)
        
        # Additional verification
        assert isinstance(result, dict)
        data_verify.verify_data_structure_classes_all_departments(result)

if __name__ == "__main__":
    pytest.main([__file__]) 