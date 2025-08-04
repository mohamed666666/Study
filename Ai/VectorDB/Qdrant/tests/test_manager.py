import unittest
from unittest.mock import patch, MagicMock
from Qdrant.managers.QdrantManager import QdrantManager

class TestQdrantManager(unittest.TestCase):
    @patch('Qdrant.managers.QdrantManager.get_qdrant_client')
    def test_get_all_points(self, mock_get_qdrant_client):
        # Mock the Qdrant client
        mock_client = MagicMock()
        mock_get_qdrant_client.return_value.__enter__.return_value = mock_client

        # Mock the scroll method response
        mock_client.scroll.side_effect = [
            MagicMock(points=[{'id': 1, 'vector': [0.1, 0.2], 'payload': {}}], next_page_offset=1),
            MagicMock(points=[{'id': 2, 'vector': [0.3, 0.4], 'payload': {}}], next_page_offset=None)
        ]

        # Create an instance of QdrantManager
        manager = QdrantManager()

        # Call the get_all_points method
        points = manager.get_all_points('test_collection')

        # Assert the results
        self.assertEqual(len(points), 2)
        self.assertEqual(points[0]['id'], 1)
        self.assertEqual(points[1]['id'], 2)

        # Ensure the scroll method was called twice
        self.assertEqual(mock_client.scroll.call_count, 2)

if __name__ == '__main__':
    unittest.main()