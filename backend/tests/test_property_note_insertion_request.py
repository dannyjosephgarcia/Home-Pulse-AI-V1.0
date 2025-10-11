import unittest
from backend.db.model.property_note_insertion_request import PropertyNoteInsertionRequest
from common.logging.error.error import Error


class TestPropertyNoteInsertionRequest(unittest.TestCase):

    def test_valid_request_with_all_fields(self):
        """Test creating a valid PropertyNoteInsertionRequest with all fields"""
        request = {
            'fileName': 'maintenance_note.txt',
            'entityType': 'appliance',
            'entityId': '123'
        }

        obj = PropertyNoteInsertionRequest(request)

        self.assertEqual(obj.file_name, 'maintenance_note.txt')
        self.assertEqual(obj.entity_type, 'appliance')
        self.assertEqual(obj.entity_id, '123')

    def test_valid_request_with_only_required_fields(self):
        """Test creating a valid PropertyNoteInsertionRequest with only fileName"""
        request = {
            'fileName': 'property_note.txt'
        }

        obj = PropertyNoteInsertionRequest(request)

        self.assertEqual(obj.file_name, 'property_note.txt')
        self.assertEqual(obj.entity_type, 'property')  # Default value
        self.assertIsNone(obj.entity_id)

    def test_valid_request_with_structure_entity_type(self):
        """Test creating request with structure entity type"""
        request = {
            'fileName': 'roof_inspection.txt',
            'entityType': 'structure',
            'entityId': '456'
        }

        obj = PropertyNoteInsertionRequest(request)

        self.assertEqual(obj.file_name, 'roof_inspection.txt')
        self.assertEqual(obj.entity_type, 'structure')
        self.assertEqual(obj.entity_id, '456')

    def test_valid_request_with_property_entity_type(self):
        """Test creating request with explicit property entity type"""
        request = {
            'fileName': 'general_note.txt',
            'entityType': 'property'
        }

        obj = PropertyNoteInsertionRequest(request)

        self.assertEqual(obj.file_name, 'general_note.txt')
        self.assertEqual(obj.entity_type, 'property')
        self.assertIsNone(obj.entity_id)

    def test_missing_file_name_field(self):
        """Test that Error is raised when fileName field is missing"""
        request = {
            'entityType': 'appliance',
            'entityId': '123'
        }

        with self.assertRaises(Error):
            PropertyNoteInsertionRequest(request)

    def test_empty_request(self):
        """Test that Error is raised when request is empty"""
        request = {}

        with self.assertRaises(Error):
            PropertyNoteInsertionRequest(request)

    def test_file_name_with_path(self):
        """Test fileName with full path"""
        request = {
            'fileName': 'notes/2024/maintenance_note.txt'
        }

        obj = PropertyNoteInsertionRequest(request)
        self.assertEqual(obj.file_name, 'notes/2024/maintenance_note.txt')

    def test_file_name_with_special_characters(self):
        """Test fileName with special characters"""
        request = {
            'fileName': 'note-2024.01.15_maintenance.txt'
        }

        obj = PropertyNoteInsertionRequest(request)
        self.assertEqual(obj.file_name, 'note-2024.01.15_maintenance.txt')

    def test_empty_file_name_string(self):
        """Test that empty fileName string is accepted"""
        request = {
            'fileName': ''
        }

        obj = PropertyNoteInsertionRequest(request)
        self.assertEqual(obj.file_name, '')
        self.assertEqual(obj.entity_type, 'property')

    def test_entity_id_with_entity_type(self):
        """Test that entityId without entityType still works"""
        request = {
            'fileName': 'note.txt',
            'entityId': '789'
        }

        obj = PropertyNoteInsertionRequest(request)
        self.assertEqual(obj.file_name, 'note.txt')
        self.assertEqual(obj.entity_type, 'property')  # Default
        self.assertEqual(obj.entity_id, '789')

    def test_numeric_entity_id(self):
        """Test that numeric entityId is accepted"""
        request = {
            'fileName': 'inspection.txt',
            'entityType': 'appliance',
            'entityId': 999
        }

        obj = PropertyNoteInsertionRequest(request)
        self.assertEqual(obj.entity_id, 999)


if __name__ == '__main__':
    unittest.main()
