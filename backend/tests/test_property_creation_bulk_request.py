import unittest
from unittest.mock import MagicMock
from backend.db.model.property_creation_bulk_request import PropertyCreationBulkRequest
from common.logging.error.error import Error


class TestPropertyCreationBulkRequest(unittest.TestCase):

    def test_valid_csv_file_request(self):
        """Test creating a valid PropertyCreationBulkRequest with CSV file"""
        mock_file = MagicMock()
        mock_file.read.return_value = b'header1,header2\nvalue1,value2'

        files = {
            'file': mock_file
        }

        obj = PropertyCreationBulkRequest(files)

        self.assertEqual(obj.csv_file, mock_file)
        self.assertEqual(obj.raw_bytes, b'header1,header2\nvalue1,value2')
        self.assertEqual(obj.text, 'header1,header2\nvalue1,value2')
        self.assertIsNotNone(obj.content)

    def test_missing_file_field(self):
        """Test that Error is raised when file field is missing"""
        files = {}

        with self.assertRaises(Error):
            PropertyCreationBulkRequest(files)

    def test_file_with_utf8_content(self):
        """Test that UTF-8 encoded CSV is properly decoded"""
        mock_file = MagicMock()
        mock_file.read.return_value = 'Property,Address\nHome,123 Main St'.encode('utf-8')

        files = {
            'file': mock_file
        }

        obj = PropertyCreationBulkRequest(files)

        self.assertEqual(obj.text, 'Property,Address\nHome,123 Main St')

    def test_empty_csv_file(self):
        """Test that empty CSV file is handled"""
        mock_file = MagicMock()
        mock_file.read.return_value = b''

        files = {
            'file': mock_file
        }

        obj = PropertyCreationBulkRequest(files)

        self.assertEqual(obj.raw_bytes, b'')
        self.assertEqual(obj.text, '')

    def test_csv_file_with_special_characters(self):
        """Test CSV file with special characters"""
        mock_file = MagicMock()
        csv_content = 'Name,Address\n"O\'Brien",123 Main St'
        mock_file.read.return_value = csv_content.encode('utf-8')

        files = {
            'file': mock_file
        }

        obj = PropertyCreationBulkRequest(files)

        self.assertEqual(obj.text, csv_content)


if __name__ == '__main__':
    unittest.main()
