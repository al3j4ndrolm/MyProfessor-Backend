import os
import pytest
import sys

from data_fetchers.schools.sjsu import terms
from tests.data_fetchers.schools.base_test import BaseSchoolTest

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

class TestSJSUTerms(BaseSchoolTest):
    @property
    def school_name(self):
        return "sjsu"
    
    @property
    def test_type(self):
        return "terms"
    
    def test_get_terms(self):
        """Test getting terms from HTML"""
        soup = self.load_test_html_data("terms_test_sample.html")
        
        def run_test():
            result = terms.get_terms(soup)
            return result
        
        # Run test with automatic result saving and data loading
        result = self.run_test_with_result_saving(run_test)
        
        # Additional verification
        assert isinstance(result, list)
        assert all(isinstance(item, dict) and "termName" in item and "termCode" in item for item in result)

if __name__ == "__main__":
    pytest.main([__file__]) 