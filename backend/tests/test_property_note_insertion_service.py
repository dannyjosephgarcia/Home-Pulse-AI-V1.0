import unittest
from unittest.mock import MagicMock, patch
from backend.db.service.property_note_insertion_service import PropertyNoteInsertionService
from common.logging.error.error import Error
from backend.db.model.query.sql_statements import INSERT_PROPERTY_NOTE


class TestPropertyNoteInsertionService(unittest.TestCase):
    """Test cases for PropertyNoteInsertionService"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_pool = MagicMock()
        self.mock_connection = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_s3_client = MagicMock()
        self.bucket_name = 'test-bucket'

        self.mock_pool.pool.get_connection.return_value = self.mock_connection
        self.mock_connection.cursor.return_value = self.mock_cursor

        self.service = PropertyNoteInsertionService(
            self.mock_pool,
            self.mock_s3_client,
            self.bucket_name
        )


class TestInsertAndSignPropertyNoteUrl(TestPropertyNoteInsertionService):
    """Tests for insert_and_sign_property_note_url method"""

    def test_insert_and_sign_property_note_url_success(self):
        """Test successful note insertion and S3 URL generation"""
        # Arrange
        user_id = 123
        property_id = 456
        entity_type = 'appliance'
        entity_id = 789
        file_name = 'maintenance_note.txt'
        expected_key = f'users/{user_id}/properties/{property_id}/notes/{file_name}'
        expected_url = f'https://s3.amazonaws.com/test-bucket/{expected_key}?signature=abc123'

        self.mock_s3_client.client.generate_presigned_url.return_value = expected_url

        # Act
        result = self.service.insert_and_sign_property_note_url(
            user_id, property_id, entity_type, entity_id, file_name
        )

        # Assert
        self.assertEqual(result['noteUrl'], expected_url)
        self.assertEqual(result['noteKey'], expected_key)
        self.assertEqual(result['putRecordStatus'], 200)

        # Verify S3 presigned URL was generated
        self.mock_s3_client.client.generate_presigned_url.assert_called_once_with(
            'put_object',
            Params={
                'Bucket': self.bucket_name,
                'Key': expected_key,
                'ContentType': 'text/plain'
            },
            ExpiresIn=600
        )

        # Verify database insert was called
        self.mock_cursor.execute.assert_called_once_with(
            INSERT_PROPERTY_NOTE,
            [user_id, property_id, entity_type, entity_id, expected_key]
        )
        self.mock_connection.commit.assert_called_once()
        self.mock_cursor.close.assert_called_once()
        self.mock_connection.close.assert_called_once()

    def test_insert_and_sign_property_note_url_property_level(self):
        """Test note insertion for property-level note (no entity_id)"""
        # Arrange
        user_id = 123
        property_id = 456
        entity_type = 'property'
        entity_id = None
        file_name = 'general_note.txt'
        expected_key = f'users/{user_id}/properties/{property_id}/notes/{file_name}'
        expected_url = f'https://s3.amazonaws.com/{expected_key}'

        self.mock_s3_client.client.generate_presigned_url.return_value = expected_url

        # Act
        result = self.service.insert_and_sign_property_note_url(
            user_id, property_id, entity_type, entity_id, file_name
        )

        # Assert
        self.assertEqual(result['noteUrl'], expected_url)
        self.assertEqual(result['noteKey'], expected_key)
        self.assertEqual(result['putRecordStatus'], 200)

        # Verify database insert was called with None for entity_id
        self.mock_cursor.execute.assert_called_once_with(
            INSERT_PROPERTY_NOTE,
            [user_id, property_id, entity_type, None, expected_key]
        )

    def test_insert_and_sign_property_note_url_structure_entity(self):
        """Test note insertion for structure entity"""
        # Arrange
        user_id = 999
        property_id = 111
        entity_type = 'structure'
        entity_id = 222
        file_name = 'roof_inspection.txt'
        expected_key = f'users/{user_id}/properties/{property_id}/notes/{file_name}'
        expected_url = f'https://s3.amazonaws.com/{expected_key}'

        self.mock_s3_client.client.generate_presigned_url.return_value = expected_url

        # Act
        result = self.service.insert_and_sign_property_note_url(
            user_id, property_id, entity_type, entity_id, file_name
        )

        # Assert
        self.assertEqual(result['noteKey'], expected_key)
        self.mock_cursor.execute.assert_called_once_with(
            INSERT_PROPERTY_NOTE,
            [user_id, property_id, entity_type, entity_id, expected_key]
        )


class TestSignPutNoteUrl(TestPropertyNoteInsertionService):
    """Tests for sign_put_note_url method"""

    def test_sign_put_note_url_success(self):
        """Test successful S3 presigned URL generation"""
        # Arrange
        note_key = 'users/123/properties/456/notes/test.txt'
        expected_url = 'https://s3.amazonaws.com/test-bucket/test.txt?signature=xyz'
        self.mock_s3_client.client.generate_presigned_url.return_value = expected_url

        # Act
        result = self.service.sign_put_note_url(note_key)

        # Assert
        self.assertEqual(result, expected_url)
        self.mock_s3_client.client.generate_presigned_url.assert_called_once_with(
            'put_object',
            Params={
                'Bucket': self.bucket_name,
                'Key': note_key,
                'ContentType': 'text/plain'
            },
            ExpiresIn=600
        )

    def test_sign_put_note_url_with_special_characters(self):
        """Test URL generation with special characters in key"""
        # Arrange
        note_key = 'users/123/properties/456/notes/note-2024_01.15.txt'
        expected_url = 'https://s3.amazonaws.com/test-bucket/note.txt'
        self.mock_s3_client.client.generate_presigned_url.return_value = expected_url

        # Act
        result = self.service.sign_put_note_url(note_key)

        # Assert
        self.assertEqual(result, expected_url)

    def test_sign_put_note_url_s3_error(self):
        """Test that S3 errors raise AWS_CONNECTION_ISSUE error"""
        # Arrange
        note_key = 'users/123/properties/456/notes/test.txt'
        self.mock_s3_client.client.generate_presigned_url.side_effect = Exception('S3 connection failed')

        # Act & Assert
        with self.assertRaises(Error) as context:
            self.service.sign_put_note_url(note_key)

        # Verify error message contains AWS_CONNECTION_ISSUE
        self.assertIsNotNone(context.exception)


class TestInsertPropertyNoteUrl(TestPropertyNoteInsertionService):
    """Tests for insert_property_note_url static method"""

    def test_insert_property_note_url_success(self):
        """Test successful database insertion of note URL"""
        # Arrange
        user_id = 123
        property_id = 456
        entity_type = 'appliance'
        entity_id = 789
        note_key = 'users/123/properties/456/notes/test.txt'

        # Act
        result = PropertyNoteInsertionService.insert_property_note_url(
            self.mock_connection, user_id, property_id, entity_type, entity_id, note_key
        )

        # Assert
        self.assertEqual(result, 200)
        self.mock_cursor.execute.assert_called_once_with(
            INSERT_PROPERTY_NOTE,
            [user_id, property_id, entity_type, entity_id, note_key]
        )
        self.mock_connection.commit.assert_called_once()
        self.mock_cursor.close.assert_called_once()

    def test_insert_property_note_url_with_none_entity_id(self):
        """Test database insertion with None entity_id"""
        # Arrange
        user_id = 123
        property_id = 456
        entity_type = 'property'
        entity_id = None
        note_key = 'users/123/properties/456/notes/test.txt'

        # Act
        result = PropertyNoteInsertionService.insert_property_note_url(
            self.mock_connection, user_id, property_id, entity_type, entity_id, note_key
        )

        # Assert
        self.assertEqual(result, 200)
        self.mock_cursor.execute.assert_called_once_with(
            INSERT_PROPERTY_NOTE,
            [user_id, property_id, entity_type, None, note_key]
        )

    def test_insert_property_note_url_db_error(self):
        """Test that database errors raise INTERNAL_SERVICE_ERROR"""
        # Arrange
        user_id = 123
        property_id = 456
        entity_type = 'appliance'
        entity_id = 789
        note_key = 'users/123/properties/456/notes/test.txt'
        self.mock_cursor.execute.side_effect = Exception('Database connection lost')

        # Act & Assert
        with self.assertRaises(Error):
            PropertyNoteInsertionService.insert_property_note_url(
                self.mock_connection, user_id, property_id, entity_type, entity_id, note_key
            )


class TestConstructS3NoteKey(TestPropertyNoteInsertionService):
    """Tests for _construct_s3_note_key static method"""

    def test_construct_s3_note_key(self):
        """Test S3 key construction with standard inputs"""
        # Arrange
        user_id = 123
        property_id = 456
        file_name = 'maintenance_note.txt'

        # Act
        result = PropertyNoteInsertionService._construct_s3_note_key(
            user_id, property_id, file_name
        )

        # Assert
        expected_key = 'users/123/properties/456/notes/maintenance_note.txt'
        self.assertEqual(result, expected_key)

    def test_construct_s3_note_key_with_path_in_filename(self):
        """Test S3 key construction when filename contains path"""
        # Arrange
        user_id = 999
        property_id = 111
        file_name = 'subfolder/note.txt'

        # Act
        result = PropertyNoteInsertionService._construct_s3_note_key(
            user_id, property_id, file_name
        )

        # Assert
        expected_key = 'users/999/properties/111/notes/subfolder/note.txt'
        self.assertEqual(result, expected_key)

    def test_construct_s3_note_key_with_special_characters(self):
        """Test S3 key construction with special characters in filename"""
        # Arrange
        user_id = 123
        property_id = 456
        file_name = 'note-2024.01.15_maintenance.txt'

        # Act
        result = PropertyNoteInsertionService._construct_s3_note_key(
            user_id, property_id, file_name
        )

        # Assert
        expected_key = 'users/123/properties/456/notes/note-2024.01.15_maintenance.txt'
        self.assertEqual(result, expected_key)

    def test_construct_s3_note_key_format(self):
        """Test that S3 key follows correct format pattern"""
        # Arrange
        user_id = 1
        property_id = 2
        file_name = 'test.txt'

        # Act
        result = PropertyNoteInsertionService._construct_s3_note_key(
            user_id, property_id, file_name
        )

        # Assert
        self.assertTrue(result.startswith('users/'))
        self.assertIn('/properties/', result)
        self.assertIn('/notes/', result)
        self.assertTrue(result.endswith(file_name))


class TestObtainConnection(TestPropertyNoteInsertionService):
    """Tests for obtain_connection method"""

    def test_obtain_connection_success(self):
        """Test successfully obtaining a database connection"""
        # Act
        result = self.service.obtain_connection()

        # Assert
        self.assertEqual(result, self.mock_connection)
        self.mock_pool.pool.get_connection.assert_called_once()

    def test_obtain_connection_error(self):
        """Test that connection pool errors raise INTERNAL_SERVICE_ERROR"""
        # Arrange
        self.mock_pool.pool.get_connection.side_effect = Exception('Connection pool exhausted')

        # Act & Assert
        with self.assertRaises(Error):
            self.service.obtain_connection()


if __name__ == '__main__':
    unittest.main()
