import os
import sys
import pytest
from unittest.mock import Mock, patch
from bs4 import Tag, BeautifulSoup

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Temporarily comment out import to fix module not found error
# from data_fetchers.ratings.rmp import _get_best_match_data, get_rmp_data
from data_fetchers.ratings.rating_configs import RMP_DEFAULTS
from helpers.data import data_keys

class TestGetRMPData:
    """Test class for get_rmp_data function"""

    def test_get_rmp_data(self):
        """Test that get_rmp_data function returns the correct data"""

        result = get_rmp_data("Brett Johnson", rmp_code="1967")

        assert result is not None
        assert result == {
            "difficulty": RMP_DEFAULTS[data_keys.PROFESSOR_DIFFICULTY_KEY],
            "rating": RMP_DEFAULTS[data_keys.PROFESSOR_RATING_KEY],
            "reviewCount": RMP_DEFAULTS[data_keys.PROFESSOR_REVIEW_COUNT_KEY],
            "recommend": RMP_DEFAULTS[data_keys.PROFESSOR_RECOMMEND_KEY],
            "link": "/professor/2942170",
            "score": 1.0,
        }

class TestRMPGetBestMatchData:
    """Test class for _get_best_match_data function"""
    
    def test_match_case_1(self):
        """Test that exact name match returns the professor element"""

        professor_elements = [
            _create_element("Jian (Andrew) Yu"),
            _create_element("Nicky Yuen"),
            _create_element("Zuleyha Yuksek"),
            _create_element("Lale Yurtseven"),
            _create_element("Linyun Yu"),
        ]
        
        # Call the function
        result = _get_best_match_data(professor_elements, "Jian Yu")
        
        # Verify result
        assert result is not None
        assert result["rmp_name"] == "Jian (Andrew) Yu"
        assert result["professor_element"] == professor_elements[0]
    
    def test_match_case_2(self):
        """Test that exact name match returns the professor element"""

        professor_elements = [
            _create_element("Jian (Andrew) Yu"),
            _create_element("Nicky Yuen"),
            _create_element("Zuleyha Yuksek"),
            _create_element("Lale Yurtseven"),
            _create_element("Linyun Yu"),
        ]
        
        # Call the function
        result = _get_best_match_data(professor_elements, "Jian Andrew Yu")
        
        # Verify result
        assert result is not None
        assert result["rmp_name"] == "Jian (Andrew) Yu"
        assert result["professor_element"] == professor_elements[0]
    
    def test_match_case_3(self):
        """Test that exact name match returns the professor element"""

        professor_elements = [
            _create_element("John Yu"),
            _create_element("Nicky Yuen"),
            _create_element("Zuleyha Yuksek"),
            _create_element("Lale Yurtseven"),
            _create_element("Linyun Yu"),
        ]
        
        # Call the function
        result = _get_best_match_data(professor_elements, "Jian Yu")
        
        # Verify result
        assert result is None
    
    def test_match_case_4(self):
        """Test that exact name match returns the professor element"""

        professor_elements = [
            _create_element("Jian Yu"),
            _create_element("Nicky Yuen"),
            _create_element("Zuleyha Yuksek"),
            _create_element("Lale Yurtseven"),
            _create_element("Linyun Yu"),
        ]
        
        # Call the function
        result = _get_best_match_data(professor_elements, "Jian Andrew Yu")
        
        # Verify result
        assert result is not None
        assert result["rmp_name"] == "Jian Yu"
        assert result["professor_element"] == professor_elements[0]
    
    def test_match_case_5(self):
        """Test middle name vs no middle name - should match"""

        professor_elements = [
            _create_element("Robert Michael Johnson"),
            _create_element("Sarah Williams"),
            _create_element("Michael Brown"),
            _create_element("Lisa Davis"),
        ]
        
        # Call the function
        result = _get_best_match_data(professor_elements, "Robert M Johnson")
        
        # Verify result
        assert result is not None
        assert result["rmp_name"] == "Robert Michael Johnson"
        assert result["professor_element"] == professor_elements[0]
    
    def test_match_case_6(self):
        """Test nickname vs full name - should match"""

        professor_elements = [
            _create_element("William (Bill) Thompson"),
            _create_element("Jennifer Smith"),
            _create_element("David Wilson"),
            _create_element("Emily Johnson"),
        ]
        
        # Call the function
        result = _get_best_match_data(professor_elements, "Bill Thompson")
        
        # Verify result
        assert result is not None
        assert result["rmp_name"] == "William (Bill) Thompson"
        assert result["professor_element"] == professor_elements[0]
    
    def test_match_case_7(self):
        """Test maiden name vs married name - should not match"""

        professor_elements = [
            _create_element("Sarah Johnson"),
            _create_element("Maria Rodriguez"),
            _create_element("David Chen"),
            _create_element("Lisa Anderson"),
        ]
        
        # Call the function
        result = _get_best_match_data(professor_elements, "Sarah Smith")
        
        # Verify result
        assert result is None
    
    def test_match_case_8(self):
        """Test initials vs full name - should match"""

        professor_elements = [
            _create_element("A. B. Rodriguez"),
            _create_element("Carlos Martinez"),
            _create_element("Elena Garcia"),
            _create_element("Miguel Lopez"),
        ]
        
        # Call the function
        result = _get_best_match_data(professor_elements, "Ana Rodriguez")
        
        # Verify result
        assert result is not None
        assert result["rmp_name"] == "A. B. Rodriguez"
        assert result["professor_element"] == professor_elements[0]
    
    def test_match_case_9(self):
        """Test hyphenated last name - should match"""

        professor_elements = [
            _create_element("Maria Garcia-Lopez"),
            _create_element("Juan Martinez"),
            _create_element("Carmen Rodriguez"),
            _create_element("Pedro Sanchez"),
        ]
        
        # Call the function
        result = _get_best_match_data(professor_elements, "Maria Garcia")
        
        # Verify result
        assert result is not None
        assert result["rmp_name"] == "Maria Garcia-Lopez"
        assert result["professor_element"] == professor_elements[0]
    
    def test_match_case_10(self):
        """Test multiple middle names - should match"""

        professor_elements = [
            _create_element("James Robert Michael Wilson"),
            _create_element("Thomas Anderson"),
            _create_element("Christopher Lee"),
            _create_element("Daniel Taylor"),
        ]
        
        # Call the function
        result = _get_best_match_data(professor_elements, "James Wilson")
        
        # Verify result
        assert result is not None
        assert result["rmp_name"] == "James Robert Michael Wilson"
        assert result["professor_element"] == professor_elements[0]
    
    def test_match_case_11(self):
        """Test Jr./Sr. suffix - should match"""

        professor_elements = [
            _create_element("Robert Johnson Jr."),
            _create_element("Michael Smith"),
            _create_element("David Brown"),
            _create_element("John Davis"),
        ]
        
        # Call the function
        result = _get_best_match_data(professor_elements, "Robert Johnson")
        
        # Verify result
        assert result is not None
        assert result["rmp_name"] == "Robert Johnson Jr."
        assert result["professor_element"] == professor_elements[0]
    
    def test_match_case_12(self):
        """Test PhD suffix - should match"""

        professor_elements = [
            _create_element("Dr. Sarah Williams"),
            _create_element("Jennifer Smith"),
            _create_element("Lisa Johnson"),
            _create_element("Emily Davis"),
        ]
        
        # Call the function
        result = _get_best_match_data(professor_elements, "Sarah Williams")
        
        # Verify result
        assert result is not None
        assert result["rmp_name"] == "Dr. Sarah Williams"
        assert result["professor_element"] == professor_elements[0]
    
    def test_match_case_13(self):
        """Test similar last names but different first names - should not match"""

        professor_elements = [
            _create_element("Michael Johnson"),
            _create_element("Sarah Johnson"),
            _create_element("David Johnson"),
            _create_element("Lisa Johnson"),
        ]
        
        # Call the function
        result = _get_best_match_data(professor_elements, "Robert Johnson")
        
        # Verify result
        assert result is None
    
    def test_match_case_14(self):
        """Test similar first names but different last names - should not match"""

        professor_elements = [
            _create_element("Michael Johnson"),
            _create_element("Michael Smith"),
            _create_element("Michael Brown"),
            _create_element("Michael Davis"),
        ]
        
        # Call the function
        result = _get_best_match_data(professor_elements, "Michael Wilson")
        
        # Verify result
        assert result is None
    
    def test_match_case_15(self):
        """Test case insensitive matching"""

        professor_elements = [
            _create_element("JOHN SMITH"),
            _create_element("Jane Doe"),
            _create_element("Bob Johnson"),
            _create_element("Alice Brown"),
        ]
        
        # Call the function
        result = _get_best_match_data(professor_elements, "john smith")
        
        # Verify result
        assert result is not None
        assert result["rmp_name"] == "JOHN SMITH"
        assert result["professor_element"] == professor_elements[0]
    
    def test_match_case_16(self):
        """Test empty professor elements list"""

        professor_elements = []
        
        # Call the function
        result = _get_best_match_data(professor_elements, "John Smith")
        
        # Verify result
        assert result is None
    
    def test_match_case_17(self):
        """Test unmatched name"""

        professor_elements = [
            _create_element("Jill Bronfman"),
        ]
        
        # Call the function
        result = _get_best_match_data(professor_elements, "Jill YochimTo")
        
        # Verify result
        assert result is None
    
    def test_match_case_18(self):
        """Test multiple similar names - should pick the best match"""

        professor_elements = [
            _create_element("John Smith"),
            _create_element("Jon Smith"),
            _create_element("John Smyth"),
            _create_element("Jane Smith"),
        ]
        
        # Call the function
        result = _get_best_match_data(professor_elements, "John Smith")
        
        # Verify result
        assert result is not None
        assert result["rmp_name"] == "John Smith"
        assert result["professor_element"] == professor_elements[0]
    
    def test_match_case_18(self):
        """Test multiple similar names - should pick the best match"""

        professor_elements = [
            _create_element("Palin Chen"),
            _create_element("David Chen"),
            _create_element("Chen Chen"),
        ]
        
        # Call the function
        result = _get_best_match_data(professor_elements, "Chen David")
        
        # Verify result
        assert result is not None
        assert result["rmp_name"] == "David Chen"
        assert result["professor_element"] == professor_elements[1]

    def test_match_case_19(self):
        """Test that the best match is picked"""

        professor_elements = [
            _create_element("Zachary Judson"),
        ]
        
        # Call the function
        result = _get_best_match_data(professor_elements, "Zack Judson")
        
        # Verify result
        assert result is not None
        assert result["rmp_name"] == "Zachary Judson"
        assert result["professor_element"] == professor_elements[0]

def _create_element(professor_name: str) -> Tag:
    html = f"""
        <a class="TeacherCard__StyledTeacherCard-syjs0d-0 eerjaA" href="/professor/2814263">
            <div class="TeacherCard__InfoRatingWrapper-syjs0d-3 kAxNBg">
                <div class="TeacherCard__NumRatingWrapper-syjs0d-2 bvYZTI">
                    <div class="CardNumRating__StyledCardNumRating-sc-17t4b9u-0 cSNjdE">
                        <div class="CardNumRating__CardNumRatingHeader-sc-17t4b9u-1 lhHpkk">QUALITY</div>
                        <div class="CardNumRating__CardNumRatingNumber-sc-17t4b9u-2 ERCLc">4.2</div>
                        <div class="CardNumRating__CardNumRatingCount-sc-17t4b9u-3 ckSFVh">42 ratings</div>
                    </div>
                </div>
                <div class="TeacherCard__CardInfo-syjs0d-1 cwMOi">
                    <div class="CardName__StyledCardName-sc-1gyrgim-0 gGdQEj">{professor_name}</div>
                    <div class="CardSchool__StyledCardSchool-sc-19lmz2k-2 irrVnX">
                        <div class="CardSchool__Department-sc-19lmz2k-0 hRJPlj">Geography</div>
                        <div class="CardSchool__School-sc-19lmz2k-1 bjvHvb">San Francisco State University</div>
                    </div>
                    <div class="CardFeedback__StyledCardFeedback-lq6nix-0 cLXvfC">
                        <div class="CardFeedback__CardFeedbackItem-lq6nix-1 bqWpYz">
                            <div class="CardFeedback__CardFeedbackNumber-lq6nix-2 iHkSBk">100%</div>
                                would take again
                        </div>
                        <div class="VerticalSeparator-sc-1l9ngcr-0 kXhgKB"></div> 
                        <div class="CardFeedback__CardFeedbackItem-lq6nix-1 bqWpYz">
                            <div class="CardFeedback__CardFeedbackNumber-lq6nix-2 iHkSBk">2.6</div>
                                level of difficulty
                        </div>
                    </div>
                </div>
            </div>
        </a>
        """
    return BeautifulSoup(html, 'html.parser')

if __name__ == "__main__":
    pytest.main([__file__]) 