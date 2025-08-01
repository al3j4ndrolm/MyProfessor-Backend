import os
import json
import pytest
from bs4 import BeautifulSoup

class BaseSchoolTest:
    """Base class for school tests with common functionality for test result management"""
    
    @property
    def school_name(self):
        """Override this property in subclasses to specify the school name"""
        raise NotImplementedError("Subclasses must override school_name property")
    
    @property
    def test_type(self):
        """Override this property in subclasses to specify the test type"""
        raise NotImplementedError("Subclasses must override test_type property")
    
    @property
    def test_samples_dir(self):
        """Get the test samples directory path for the specific school"""
        return os.path.join(os.path.dirname(__file__), "..", "..", "test_samples", self.school_name)
    
    @property
    def reference_filename(self):
        """Get the reference filename based on test type"""
        return f"{self.test_type}_test_reference.json"
    
    def load_test_session_data(self):
        """Load test session data from JSON file"""
        test_data_path = os.path.join(self.test_samples_dir, "schedules_test_sample.json")
        with open(test_data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_test_html_data(self, filename):
        """Load test HTML data from file"""
        html_path = os.path.join(self.test_samples_dir, filename)
        with open(html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        return BeautifulSoup(html, 'html.parser')
    
    def load_expected_data(self, reference_filename=None, key=None):
        """Load expected data from reference JSON file"""
        if reference_filename is None:
            reference_filename = self.reference_filename
        
        reference_path = os.path.join(self.test_samples_dir, reference_filename)
        with open(reference_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # If a key is specified, return that specific data
        if key and key in data:
            return data[key]
        return data
    
    def save_test_result(self, result, filename=None):
        """Save test result to JSON file"""
        if filename is None:
            filename = f"{self.test_type}_test_result.json"
        
        result_path = os.path.join(self.test_samples_dir, filename)
        
        # Convert set to list for JSON serialization if needed
        if isinstance(result, set):
            result_to_save = list(result)
        else:
            result_to_save = result
            
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(result_to_save, f, indent=2, ensure_ascii=False)
    
    def delete_test_result(self, filename=None):
        """Delete test result file"""
        if filename is None:
            filename = f"{self.test_type}_test_result.json"
        
        result_path = os.path.join(self.test_samples_dir, filename)
        if os.path.exists(result_path):
            os.remove(result_path)
    
    def run_test_with_result_saving(self, test_func, expected_data=None, reference_filename=None):
        """
        Run a test with automatic result saving and cleanup
        
        Args:
            test_func: Function that returns the test result
            expected_data: Expected data to compare against (auto-loaded if None)
            reference_filename: Name of the reference file for debugging (auto-generated if None)
        """
        result = test_func()
        
        # Save the actual result to a file
        self.save_test_result(result)
        
        # Auto-load expected data if not provided
        if expected_data is None:
            expected_data = self.load_expected_data(reference_filename)
        
        # Auto-generate reference filename if not provided
        if reference_filename is None:
            reference_filename = self.reference_filename
        
        try:
            # Check that we got the expected data
            assert result == expected_data
            
            # If all assertions pass, delete the result file
            self.delete_test_result()
            
            return result
            
        except AssertionError:
            # If test fails, leave the result file for debugging
            print(f"Test failed. Actual result saved to {self.test_type}_test_result.json for comparison.")
            print(f"Reference data is in {reference_filename}")
            raise 