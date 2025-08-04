import os
import pytest
import sys

from data_fetchers.schools.foothill import schedules
from tests import data_verify
from tests.data_fetchers.schools.base_test import BaseSchoolTest

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) )

class TestFoothillSchedules(BaseSchoolTest):
    @property
    def school_name(self):
        return "foothill"
    
    @property
    def test_type(self):
        return "schedules"
    
    def test_get_classes_per_department(self):
        """Test getting schedules from HTML"""
        soup = self.load_test_html_data("schedules_test_sample.html")
        
        def run_test():
            result = schedules.get_classes_per_department(soup)
            return result
        
        # Run test with automatic result saving and data loading
        result = self.run_test_with_result_saving(run_test)
        
        # Additional verification
        assert isinstance(result, dict)
        data_verify.verify_data_structure_classes_per_department(result)

if __name__ == "__main__":
    pytest.main([__file__]) 