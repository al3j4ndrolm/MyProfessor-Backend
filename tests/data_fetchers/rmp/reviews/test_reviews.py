import os
import sys
import pytest
from pathlib import Path

# Add the parent directory to the path so we can import the modules
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from data_fetchers.rmp.reviews.reviews import get_reviews, setup_request_session


class TestGetReviews:
    """Test class for get_reviews function"""

    def test_get_reviews_returns_list_for_valid_professor(self):
        """Test that get_reviews returns a list of review dicts for a professor with ratings"""

        session = setup_request_session()
        reviews = get_reviews("professor/89065", session)

        assert isinstance(reviews, list)
        assert len(reviews) > 0

        review = reviews[0]
        assert "id" in review
        assert "comment" in review
        assert "class" in review
        assert "ratingTags" in review
        assert "date" in review
        assert "grade" in review
        assert "difficultyRating" in review
        assert "helpfulRating" in review
        assert "isForCredit" in review
        assert "isForOnlineClass" in review

    def test_get_reviews_returns_empty_dict_for_invalid_professor(self):
        """Test that get_reviews returns an empty dict when the professor node cannot be found"""

        session = setup_request_session()
        reviews = get_reviews("professor/0", session)

        assert reviews == {}


if __name__ == "__main__":
    pytest.main([__file__])
