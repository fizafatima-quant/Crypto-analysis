# test_fork_detector.py
import unittest
from unittest.mock import patch
from fork_detector import get_recent_forks

class TestForkDetector(unittest.TestCase):
    @patch('requests.get')
    def test_empty_response(self, mock_get):
        mock_get.return_value.json.return_value = []
        self.assertEqual(get_recent_forks(), [])

    @patch('requests.get')
    def test_api_failure(self, mock_get):
        mock_get.side_effect = Exception("API down")
        self.assertEqual(get_recent_forks(), [])

    @patch('requests.get')
    def test_tvl_filtering(self, mock_get):
        mock_data = [
            {'name': 'Fork1', 'tvl': 2_000_000, 'forkedFrom': 'Original'},
            {'name': 'Fork2', 'tvl': 500_000, 'forkedFrom': 'Original'}
        ]
        mock_get.return_value.json.return_value = mock_data
        results = get_recent_forks(min_tvl=1_000_000)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'Fork1')

if __name__ == '__main__':
    unittest.main()