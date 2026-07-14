import os
import sys
import pytest
from unittest.mock import Mock

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.broadcasts_db import get_active
from database import db_keys

class TestBroadcastsDB:
    """Test class for broadcasts_db functions"""

    def test_get_active_filters_by_active_status(self):
        """Test that get_active only returns broadcasts with is_active True"""

        mock_supabase = Mock()
        mock_response = Mock()
        mock_response.data = [{"id": 1, "text": "Broadcast 1", "is_active": True}]

        mock_table = Mock()
        mock_select = Mock()
        mock_eq = Mock()

        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.eq.return_value = mock_eq
        mock_eq.execute.return_value = mock_response

        result = get_active(mock_supabase)

        mock_supabase.table.assert_called_once_with("broadcasts")
        mock_table.select.assert_called_once_with("*")
        mock_select.eq.assert_called_once_with(db_keys.BROADCAST_KEY_ACTIVE, True)
        mock_eq.execute.assert_called_once()
        assert result == mock_response.data

    def test_get_active_returns_empty_list_when_none_active(self):
        """Test that get_active returns an empty list when no broadcasts are active"""

        mock_supabase = Mock()
        mock_response = Mock()
        mock_response.data = []

        mock_table = Mock()
        mock_select = Mock()
        mock_eq = Mock()

        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.eq.return_value = mock_eq
        mock_eq.execute.return_value = mock_response

        result = get_active(mock_supabase)

        assert result == []

if __name__ == "__main__":
    pytest.main([__file__])
