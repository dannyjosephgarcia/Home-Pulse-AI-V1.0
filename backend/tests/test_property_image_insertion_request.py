import unittest
from backend.db.model.property_image_insertion_request import PropertyImageInsertionRequest
from common.logging.error.error import Error


class TestPropertyImageInsertionRequest(unittest.TestCase):

    def test_valid_request(self):
        """Test creating a valid PropertyImageInsertionRequest"""
        request = {
            'fileName': 'property_image.jpg'
        }

        obj = PropertyImageInsertionRequest(request)

        self.assertEqual(obj.file_name, 'property_image.jpg')

    def test_missing_file_name_field(self):
        """Test that Error is raised when fileName field is missing"""
        request = {}

        with self.assertRaises(Error):
            PropertyImageInsertionRequest(request)

    def test_file_name_with_path(self):
        """Test fileName with full path"""
        request = {
            'fileName': 'uploads/images/property_123.png'
        }

        obj = PropertyImageInsertionRequest(request)
        self.assertEqual(obj.file_name, 'uploads/images/property_123.png')

    def test_file_name_with_special_characters(self):
        """Test fileName with special characters"""
        request = {
            'fileName': 'property-image_2024.01.15.jpg'
        }

        obj = PropertyImageInsertionRequest(request)
        self.assertEqual(obj.file_name, 'property-image_2024.01.15.jpg')

    def test_empty_file_name(self):
        """Test that empty fileName string is accepted"""
        request = {
            'fileName': ''
        }

        obj = PropertyImageInsertionRequest(request)
        self.assertEqual(obj.file_name, '')


if __name__ == '__main__':
    unittest.main()
