import os
import pytest
import sys

from data_fetchers.schools.sfsu import courses
from tests import data_verify

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) )

def get_expected_math_courses():
    """Expected MATH courses for term 2257"""
    return {
        'MATH 107 - Mathematics for Business Calculus I',
        'MATH 110 - Business Calculus',
        'MATH 123 - Mathematics for Elementary Statistics',
        'MATH 124 - Elementary Statistics',
        'MATH 165 - Concepts of the Number System',
        'MATH 197 - Prelude to Calculus I',
        'MATH 198 - Prelude to Calculus II',
        'MATH 199 - Pre-Calculus',
        'MATH 209 - Mathematical Computing',
        'MATH 225 - Introduction to Linear Algebra',
        'MATH 226 - Calculus I',
        'MATH 227 - Calculus II',
        'MATH 228 - Calculus III',
        'MATH 245 - Elementary Differential Equations and Linear Algebra',
        'MATH 301GW - Exploration and Proof - GWAR',
        'MATH 310 - Elementary Number Theory',
        'MATH 324 - Probability and Statistics with Computing',
        'MATH 325 - Linear Algebra',
        'MATH 335 - Modern Algebra',
        'MATH 370 - Real Analysis I',
        'MATH 376 - Ordinary Differential Equations I',
        'MATH 400 - Numerical Analysis',
        'MATH 425 - Applied and Computational Linear Algebra',
        'MATH 435 - Modern Algebra II',
        'MATH 440 - Probability and Statistics I',
        'MATH 441 - Probability and Statistics II',
        'MATH 443 - Introduction to Time Series Analysis',
        'MATH 447 - Design and Analysis of Experiments',
        'MATH 448 - Introduction to Statistical Learning and Data Mining',
        'MATH 470 - Real Analysis II: Several Variables',
        'MATH 495 - Introduction to Wavelets and Frames with Applications',
        'MATH 696 - Applied Mathematics Project I',
        'MATH 697 - Applied Mathematics Project II',
        'MATH 699 - Independent Study',
        'MATH 700 - Graduate Teaching Workshop',
        'MATH 725 - Advanced Linear Algebra',
        'MATH 735 - Modern Algebra II',
        'MATH 741 - Probability and Statistics II',
        'MATH 742 - Advanced Probability Models',
        'MATH 747 - Design and Analysis of Experiments',
        'MATH 761 - Computational Statistics',
        'MATH 770 - Real Analysis II: Several Variables',
        'MATH 790 - Advanced Topics in Mathematics  (Topic: Algebraic Topology)',
        'MATH 892 - Data Science Internship',
        'MATH 895 - Research Project',
        'MATH 896EXM - Culminating Experience Examination',
        "MATH 898 - Master's Thesis",
        'MATH 899 - Independent Study'
    }

class TestSFSUCourses:
    def test_update_courses_set_per_department_math(self):
        """Test getting MATH courses for term 2257"""
        department_code = "MATH"
        term_code = "2257"
        courses_set = set()
        
        result = courses.update_courses_set_per_department(department_code, term_code, courses_set)
        expected = get_expected_math_courses()
        
        # Check that we got the expected courses
        assert result == expected
        
        # Check that the result is a set
        assert isinstance(result, set)
        
        # Check that all courses contain the department code
        for course in result:
            assert department_code in course, f"Course {course} should contain department code {department_code}"
            
        # Check that we have a reasonable number of courses (not empty, not too many)
        assert len(result) > 0, "Should have at least one course"
        assert len(result) <= 50, f"Should have reasonable number of courses, got {len(result)}"
        
        # Verify the data structure
        assert isinstance(result, set)
        data_verify.verify_data_structure_courses_set(result)

if __name__ == "__main__":
    pytest.main([__file__]) 