import os
import pytest
import sys

from data_fetchers.school_data.schools.sfsu import schedules
from tests import data_verify
from tests.data_fetchers.schools.base_test import BaseSchoolTest

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) )

class TestSFSUSchedules(BaseSchoolTest):
    @property
    def school_name(self):
        return "sfsu"
    
    @property
    def test_type(self):
        return "schedules"
    
    def test_get_classes_per_department_phys(self):
        """Test getting PHYS classes for term 2257"""
        session_data = self.load_test_session_data()
        
        def run_test():
            result = schedules.get_classes_per_department(session_data, "PHYS")
            return result
        
        # Run test with automatic result saving and data loading
        result = self.run_test_with_result_saving(run_test)
        
        # Additional verification
        assert isinstance(result, dict)
        data_verify.verify_data_structure_classes_per_department(result)

if __name__ == "__main__":
    pytest.main([__file__]) 