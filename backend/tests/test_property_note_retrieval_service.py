import unittest
from unittest.mock import MagicMock, Mock
from datetime import datetime
from backend.db.service.property_note_retrieval_service import PropertyNoteRetrievalService
from common.logging.error.error import Error
from backend.db.model.query.sql_statements import FETCH_PROPERTY_NOTES


class TestPropertyNoteRetrievalService(unittest.TestCase):
    """Test cases for PropertyNoteRetrievalService"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_pool = MagicMock()
        self.mock_connection = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_s3_client = MagicMock()
        self.bucket_name = 'test-bucket'

        self.mock_pool.pool.get_connection.return_value = self.mock_connection
        self.mock_connection.cursor.return_value = self.mock_cursor

        self.service = PropertyNoteRetrievalService(
            self.mock_pool,
            self.mock_s3_client,
            self.bucket_name
        )


class TestFetchPropertyNotesWithContent(TestPropertyNoteRetrievalService):
    """Tests for fetch_property_notes_with_content method"""

    def test_fetch_property_notes_with_content_success(self):
        """Test successful retrieval of notes with content from S3"""
        # Arrange
        property_id = 456
        user_id = 123
        created_at = datetime(2024, 1, 15, 10, 30, 0)
        updated_at = datetime(2024, 1, 16, 14, 45, 0)

        # Mock database response
        note_records = [
            (1, property_id, user_id, 'appliance', 789, 'users/123/properties/456/notes/note1.txt', created_at, updated_at),
            (2, property_id, user_id, 'property', None, 'users/123/properties/456/notes/note2.txt', created_at, updated_at)
        ]
        self.mock_cursor.fetchall.return_value = note_records

        # Mock S3 responses
        def mock_get_object(**kwargs):
            key = kwargs['Key']
            mock_response = MagicMock()
            if 'note1.txt' in key:
                mock_response['Body'].read.return_value = b'Appliance maintenance notes'
            else:
                mock_response['Body'].read.return_value = b'General property notes'
            return mock_response

        self.mock_s3_client.client.get_object.side_effect = mock_get_object

        # Act
        result = self.service.fetch_property_notes_with_content(property_id, user_id)

        # Assert
        self.assertIn('notes', result)
        self.assertEqual(len(result['notes']), 2)

        # Verify first note
        note1 = result['notes'][0]
        self.assertEqual(note1['id'], 1)
        self.assertEqual(note1['propertyId'], property_id)
        self.assertEqual(note1['userId'], user_id)
        self.assertEqual(note1['entityType'], 'appliance')
        self.assertEqual(note1['entityId'], 789)
        self.assertEqual(note1['filePath'], 'users/123/properties/456/notes/note1.txt')
        self.assertEqual(note1['content'], 'Appliance maintenance notes')
        self.assertEqual(note1['createdAt'], '2024-01-15T10:30:00')
        self.assertEqual(note1['updatedAt'], '2024-01-16T14:45:00')

        # Verify second note
        note2 = result['notes'][1]
        self.assertEqual(note2['entityType'], 'property')
        self.assertIsNone(note2['entityId'])
        self.assertEqual(note2['content'], 'General property notes')

        # Verify S3 was called twice
        self.assertEqual(self.mock_s3_client.client.get_object.call_count, 2)
        self.mock_connection.close.assert_called_once()

    def test_fetch_property_notes_with_entity_type_filter(self):
        """Test retrieval with entity_type filter"""
        # Arrange
        property_id = 456
        user_id = 123
        entity_type = 'appliance'
        created_at = datetime(2024, 1, 15)
        updated_at = datetime(2024, 1, 16)

        # Mock database response
        note_records = [
            (1, property_id, user_id, 'appliance', 789, 'users/123/properties/456/notes/note1.txt', created_at, updated_at)
        ]
        self.mock_cursor.fetchall.return_value = note_records

        # Mock S3 response
        mock_response = MagicMock()
        mock_response['Body'].read.return_value = b'Appliance note content'
        self.mock_s3_client.client.get_object.return_value = mock_response

        # Act
        result = self.service.fetch_property_notes_with_content(
            property_id, user_id, entity_type=entity_type
        )

        # Assert
        self.assertEqual(len(result['notes']), 1)
        self.assertEqual(result['notes'][0]['entityType'], 'appliance')

        # Verify SQL query includes entity_type filter
        executed_query = self.mock_cursor.execute.call_args[0][0]
        executed_params = self.mock_cursor.execute.call_args[0][1]
        self.assertIn('AND entity_type = %s', executed_query)
        self.assertEqual(executed_params[2], 'appliance')

    def test_fetch_property_notes_with_entity_id_filter(self):
        """Test retrieval with entity_id filter"""
        # Arrange
        property_id = 456
        user_id = 123
        entity_id = 789
        created_at = datetime(2024, 1, 15)
        updated_at = datetime(2024, 1, 16)

        # Mock database response
        note_records = [
            (1, property_id, user_id, 'appliance', 789, 'users/123/properties/456/notes/note1.txt', created_at, updated_at)
        ]
        self.mock_cursor.fetchall.return_value = note_records

        # Mock S3 response
        mock_response = MagicMock()
        mock_response['Body'].read.return_value = b'Specific appliance note'
        self.mock_s3_client.client.get_object.return_value = mock_response

        # Act
        result = self.service.fetch_property_notes_with_content(
            property_id, user_id, entity_id=entity_id
        )

        # Assert
        self.assertEqual(len(result['notes']), 1)
        self.assertEqual(result['notes'][0]['entityId'], 789)

        # Verify SQL query includes entity_id filter
        executed_query = self.mock_cursor.execute.call_args[0][0]
        executed_params = self.mock_cursor.execute.call_args[0][1]
        self.assertIn('AND entity_id = %s', executed_query)
        self.assertEqual(executed_params[2], 789)

    def test_fetch_property_notes_with_both_filters(self):
        """Test retrieval with both entity_type and entity_id filters"""
        # Arrange
        property_id = 456
        user_id = 123
        entity_type = 'structure'
        entity_id = 999
        created_at = datetime(2024, 1, 15)
        updated_at = datetime(2024, 1, 16)

        # Mock database response
        note_records = [
            (1, property_id, user_id, 'structure', 999, 'users/123/properties/456/notes/roof.txt', created_at, updated_at)
        ]
        self.mock_cursor.fetchall.return_value = note_records

        # Mock S3 response
        mock_response = MagicMock()
        mock_response['Body'].read.return_value = b'Roof inspection notes'
        self.mock_s3_client.client.get_object.return_value = mock_response

        # Act
        result = self.service.fetch_property_notes_with_content(
            property_id, user_id, entity_type=entity_type, entity_id=entity_id
        )

        # Assert
        self.assertEqual(len(result['notes']), 1)
        self.assertEqual(result['notes'][0]['entityType'], 'structure')
        self.assertEqual(result['notes'][0]['entityId'], 999)

        # Verify SQL query includes both filters
        executed_query = self.mock_cursor.execute.call_args[0][0]
        executed_params = self.mock_cursor.execute.call_args[0][1]
        self.assertIn('AND entity_type = %s', executed_query)
        self.assertIn('AND entity_id = %s', executed_query)
        self.assertEqual(executed_params[2], 'structure')
        self.assertEqual(executed_params[3], 999)

    def test_fetch_property_notes_no_results(self):
        """Test retrieval when no notes exist"""
        # Arrange
        property_id = 456
        user_id = 123
        self.mock_cursor.fetchall.return_value = []

        # Act
        result = self.service.fetch_property_notes_with_content(property_id, user_id)

        # Assert
        self.assertIn('notes', result)
        self.assertEqual(len(result['notes']), 0)
        self.assertEqual(result['notes'], [])

        # Verify S3 was not called
        self.mock_s3_client.client.get_object.assert_not_called()
        self.mock_connection.close.assert_called_once()

    def test_fetch_property_notes_s3_file_not_found(self):
        """Test handling when S3 file doesn't exist (NoSuchKey)"""
        # Arrange
        property_id = 456
        user_id = 123
        created_at = datetime(2024, 1, 15)
        updated_at = datetime(2024, 1, 16)

        # Mock database response
        note_records = [
            (1, property_id, user_id, 'property', None, 'users/123/properties/456/notes/missing.txt', created_at, updated_at)
        ]
        self.mock_cursor.fetchall.return_value = note_records

        # Create a custom NoSuchKey exception class
        class NoSuchKey(Exception):
            pass

        # Mock S3 NoSuchKey exception
        self.mock_s3_client.client.exceptions.NoSuchKey = NoSuchKey
        self.mock_s3_client.client.get_object.side_effect = NoSuchKey('File not found')

        # Act
        result = self.service.fetch_property_notes_with_content(property_id, user_id)

        # Assert
        self.assertEqual(len(result['notes']), 1)
        self.assertIsNone(result['notes'][0]['content'])  # Content should be None when file not found

    def test_fetch_property_notes_s3_error(self):
        """Test that S3 errors raise AWS_CONNECTION_ISSUE"""
        # Arrange
        property_id = 456
        user_id = 123
        created_at = datetime(2024, 1, 15)
        updated_at = datetime(2024, 1, 16)

        # Mock database response
        note_records = [
            (1, property_id, user_id, 'property', None, 'users/123/properties/456/notes/note.txt', created_at, updated_at)
        ]
        self.mock_cursor.fetchall.return_value = note_records

        # Mock S3 error (not NoSuchKey)
        self.mock_s3_client.client.exceptions.NoSuchKey = type('NoSuchKey', (Exception,), {})
        self.mock_s3_client.client.get_object.side_effect = Exception('S3 connection timeout')

        # Act & Assert
        with self.assertRaises(Error):
            self.service.fetch_property_notes_with_content(property_id, user_id)

    def test_fetch_property_notes_with_none_timestamps(self):
        """Test handling notes with None timestamps"""
        # Arrange
        property_id = 456
        user_id = 123

        # Mock database response with None timestamps
        note_records = [
            (1, property_id, user_id, 'property', None, 'users/123/properties/456/notes/note.txt', None, None)
        ]
        self.mock_cursor.fetchall.return_value = note_records

        # Mock S3 response
        mock_response = MagicMock()
        mock_response['Body'].read.return_value = b'Note content'
        self.mock_s3_client.client.get_object.return_value = mock_response

        # Act
        result = self.service.fetch_property_notes_with_content(property_id, user_id)

        # Assert
        self.assertIsNone(result['notes'][0]['createdAt'])
        self.assertIsNone(result['notes'][0]['updatedAt'])


class TestFetchNoteContentFromS3(TestPropertyNoteRetrievalService):
    """Tests for fetch_note_content_from_s3 method"""

    def test_fetch_note_content_from_s3_success(self):
        """Test successful content retrieval from S3"""
        # Arrange
        file_path = 'users/123/properties/456/notes/test.txt'
        expected_content = 'This is test note content'

        mock_response = MagicMock()
        mock_response['Body'].read.return_value = expected_content.encode('utf-8')
        self.mock_s3_client.client.get_object.return_value = mock_response

        # Act
        result = self.service.fetch_note_content_from_s3(file_path)

        # Assert
        self.assertEqual(result, expected_content)
        self.mock_s3_client.client.get_object.assert_called_once_with(
            Bucket=self.bucket_name,
            Key=file_path
        )

    def test_fetch_note_content_with_multiline_text(self):
        """Test fetching multiline content from S3"""
        # Arrange
        file_path = 'users/123/properties/456/notes/multiline.txt'
        expected_content = 'Line 1\nLine 2\nLine 3'

        mock_response = MagicMock()
        mock_response['Body'].read.return_value = expected_content.encode('utf-8')
        self.mock_s3_client.client.get_object.return_value = mock_response

        # Act
        result = self.service.fetch_note_content_from_s3(file_path)

        # Assert
        self.assertEqual(result, expected_content)

    def test_fetch_note_content_with_unicode(self):
        """Test fetching content with unicode characters"""
        # Arrange
        file_path = 'users/123/properties/456/notes/unicode.txt'
        expected_content = 'Note with unicode: café, naïve, 日本語'

        mock_response = MagicMock()
        mock_response['Body'].read.return_value = expected_content.encode('utf-8')
        self.mock_s3_client.client.get_object.return_value = mock_response

        # Act
        result = self.service.fetch_note_content_from_s3(file_path)

        # Assert
        self.assertEqual(result, expected_content)

    def test_fetch_note_content_file_not_found(self):
        """Test handling when file doesn't exist in S3"""
        # Arrange
        file_path = 'users/123/properties/456/notes/missing.txt'
        self.mock_s3_client.client.exceptions.NoSuchKey = type('NoSuchKey', (Exception,), {})
        self.mock_s3_client.client.get_object.side_effect = self.mock_s3_client.client.exceptions.NoSuchKey('Not found')

        # Act
        result = self.service.fetch_note_content_from_s3(file_path)

        # Assert
        self.assertIsNone(result)

    def test_fetch_note_content_s3_error(self):
        """Test that S3 errors raise AWS_CONNECTION_ISSUE"""
        # Arrange
        file_path = 'users/123/properties/456/notes/test.txt'
        self.mock_s3_client.client.exceptions.NoSuchKey = type('NoSuchKey', (Exception,), {})
        self.mock_s3_client.client.get_object.side_effect = Exception('S3 service unavailable')

        # Act & Assert
        with self.assertRaises(Error):
            self.service.fetch_note_content_from_s3(file_path)


class TestRetrievePropertyNoteRecords(TestPropertyNoteRetrievalService):
    """Tests for retrieve_property_note_records static method"""

    def test_retrieve_property_note_records_success(self):
        """Test successful database query for note records"""
        # Arrange
        property_id = 456
        user_id = 123
        created_at = datetime(2024, 1, 15)
        updated_at = datetime(2024, 1, 16)

        expected_records = [
            (1, property_id, user_id, 'appliance', 789, 'users/123/properties/456/notes/note1.txt', created_at, updated_at),
            (2, property_id, user_id, 'property', None, 'users/123/properties/456/notes/note2.txt', created_at, updated_at)
        ]
        self.mock_cursor.fetchall.return_value = expected_records

        # Act
        result = PropertyNoteRetrievalService.retrieve_property_note_records(
            self.mock_connection, property_id, user_id
        )

        # Assert
        self.assertEqual(result, expected_records)

        # Verify query includes ORDER BY clause
        executed_query = self.mock_cursor.execute.call_args[0][0]
        self.assertIn(FETCH_PROPERTY_NOTES, executed_query)
        self.assertIn('ORDER BY created_at DESC', executed_query)

        # Verify parameters
        executed_params = self.mock_cursor.execute.call_args[0][1]
        self.assertEqual(executed_params[0], property_id)
        self.assertEqual(executed_params[1], user_id)

        self.mock_cursor.close.assert_called_once()

    def test_retrieve_property_note_records_with_entity_type_filter(self):
        """Test database query with entity_type filter"""
        # Arrange
        property_id = 456
        user_id = 123
        entity_type = 'structure'

        self.mock_cursor.fetchall.return_value = []

        # Act
        PropertyNoteRetrievalService.retrieve_property_note_records(
            self.mock_connection, property_id, user_id, entity_type=entity_type
        )

        # Assert
        executed_query = self.mock_cursor.execute.call_args[0][0]
        executed_params = self.mock_cursor.execute.call_args[0][1]

        self.assertIn('AND entity_type = %s', executed_query)
        self.assertEqual(len(executed_params), 3)
        self.assertEqual(executed_params[2], 'structure')

    def test_retrieve_property_note_records_with_entity_id_filter(self):
        """Test database query with entity_id filter"""
        # Arrange
        property_id = 456
        user_id = 123
        entity_id = 789

        self.mock_cursor.fetchall.return_value = []

        # Act
        PropertyNoteRetrievalService.retrieve_property_note_records(
            self.mock_connection, property_id, user_id, entity_id=entity_id
        )

        # Assert
        executed_query = self.mock_cursor.execute.call_args[0][0]
        executed_params = self.mock_cursor.execute.call_args[0][1]

        self.assertIn('AND entity_id = %s', executed_query)
        self.assertEqual(len(executed_params), 3)
        self.assertEqual(executed_params[2], 789)

    def test_retrieve_property_note_records_with_both_filters(self):
        """Test database query with both filters"""
        # Arrange
        property_id = 456
        user_id = 123
        entity_type = 'appliance'
        entity_id = 789

        self.mock_cursor.fetchall.return_value = []

        # Act
        PropertyNoteRetrievalService.retrieve_property_note_records(
            self.mock_connection, property_id, user_id,
            entity_type=entity_type, entity_id=entity_id
        )

        # Assert
        executed_query = self.mock_cursor.execute.call_args[0][0]
        executed_params = self.mock_cursor.execute.call_args[0][1]

        self.assertIn('AND entity_type = %s', executed_query)
        self.assertIn('AND entity_id = %s', executed_query)
        self.assertEqual(len(executed_params), 4)
        self.assertEqual(executed_params[2], 'appliance')
        self.assertEqual(executed_params[3], 789)

    def test_retrieve_property_note_records_empty_result(self):
        """Test handling empty query results"""
        # Arrange
        property_id = 456
        user_id = 123
        self.mock_cursor.fetchall.return_value = []

        # Act
        result = PropertyNoteRetrievalService.retrieve_property_note_records(
            self.mock_connection, property_id, user_id
        )

        # Assert
        self.assertEqual(result, [])

    def test_retrieve_property_note_records_db_error(self):
        """Test that database errors raise INTERNAL_SERVICE_ERROR"""
        # Arrange
        property_id = 456
        user_id = 123
        self.mock_cursor.execute.side_effect = Exception('Database query failed')

        # Act & Assert
        with self.assertRaises(Error):
            PropertyNoteRetrievalService.retrieve_property_note_records(
                self.mock_connection, property_id, user_id
            )


class TestObtainConnection(TestPropertyNoteRetrievalService):
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
