import os
import pytest
import sys

from data_fetchers.school_data.foothill import departments
from tests.data_fetchers.schools.base_test import BaseSchoolTest

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) )

class TestFoothillDepartments(BaseSchoolTest):
    @property
    def school_name(self):
        return "foothill"
    
    @property
    def test_type(self):
        return "departments"
    
    def test_get_department_data_table(self):
        """Test getting departments from HTML"""
        soup = self.load_test_html_data("terms_test_sample.html")
        
        def run_test():
            result = departments.get_department_data_table(soup)
            return result
        
        # Run test with automatic result saving and data loading
        result = self.run_test_with_result_saving(run_test)
        
        # Additional verification
        assert isinstance(result, dict)
        assert all(isinstance(key, str) and isinstance(value, str) for key, value in result.items())

if __name__ == "__main__":
    pytest.main([__file__]) 