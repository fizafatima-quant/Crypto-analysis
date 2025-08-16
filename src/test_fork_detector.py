import unittest
from unittest.mock import patch, MagicMock
from fork_detector import get_recent_forks
import requests

class TestForkDetector(unittest.TestCase):
    
    @patch('requests.get')
    def test_rate_limiting(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout("Simulated timeout")
        with self.assertRaises(requests.exceptions.Timeout):
            get_recent_forks()
        self.assertEqual(mock_get.call_count, 3)
    
    @patch('requests.get')
    def test_empty_response(self, mock_get):
        mock_get.return_value = MagicMock(
            json=MagicMock(return_value=[]),
            status_code=200
        )
        self.assertEqual(get_recent_forks(), [])
    
    @patch('requests.get')
    def test_tvl_filtering(self, mock_get):
        mock_get.return_value = MagicMock(
            json=MagicMock(return_value=[
                {'name': 'TestFork', 'tvl': '2,000,000', 'forkedFrom': 'Original'},
                {'name': 'SmallFork', 'tvl': '500,000', 'forkedFrom': 'Original'}
            ]),
            status_code=200
        )
        result = get_recent_forks(min_tvl=1000000)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'TestFork')

if __name__ == '__main__':
    unittest.main()