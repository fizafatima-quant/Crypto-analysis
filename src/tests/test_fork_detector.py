from fork_detector import get_recent_forks
from unittest.mock import patch

def test_api_failure():
    with patch('requests.get') as mock_get:
        mock_get.side_effect = Exception("API down")
        assert get_recent_forks() == []