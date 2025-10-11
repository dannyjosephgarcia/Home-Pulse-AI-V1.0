import logging
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error_messages import INTERNAL_SERVICE_ERROR, AWS_CONNECTION_ISSUE
from common.logging.error.error import Error
from backend.db.model.query.sql_statements import FETCH_PROPERTY_NOTES


class PropertyNoteRetrievalService:
    def __init__(self, hp_ai_connection_pool, s3_client, bucket_name):
        self.pool = hp_ai_connection_pool.pool
        self.s3_client = s3_client.client
        self.bucket_name = bucket_name

    def fetch_property_notes_with_content(self, property_id, user_id, entity_type=None, entity_id=None):
        """
        Retrieves the property notes from the database and fetches their content from S3
        :param property_id: The id of the property
        :param user_id: The internal id of a user in our system
        :param entity_type: Optional filter by entity type
        :param entity_id: Optional filter by entity id
        :return: python list of dicts
        """
        logging.info(START_OF_METHOD)
        cnx = self.obtain_connection()
        note_records = self.retrieve_property_note_records(
            cnx=cnx,
            property_id=property_id,
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id)
        cnx.close()

        notes_with_content = []
        for record in note_records:
            note_id, prop_id, usr_id, ent_type, ent_id, file_path, created_at, updated_at = record

            # Fetch the note content from S3
            note_content = self.fetch_note_content_from_s3(file_path=file_path)

            note_dict = {
                'id': note_id,
                'propertyId': prop_id,
                'userId': usr_id,
                'entityType': ent_type,
                'entityId': ent_id,
                'filePath': file_path,
                'content': note_content,
                'createdAt': created_at.isoformat() if created_at else None,
                'updatedAt': updated_at.isoformat() if updated_at else None
            }
            notes_with_content.append(note_dict)

        logging.info(END_OF_METHOD)
        return {'notes': notes_with_content}

    def fetch_note_content_from_s3(self, file_path):
        """
        Fetches the note content from S3
        :param file_path: The S3 key where the note is stored
        :return: python str, the note content
        """
        logging.info(START_OF_METHOD)
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
            content = response['Body'].read().decode('utf-8')
            logging.info(END_OF_METHOD)
            return content
        except self.s3_client.exceptions.NoSuchKey:
            logging.warning(f'Note file not found in S3: {file_path}')
            return None
        except Exception as e:
            logging.error('An issue occurred fetching note content from S3',
                          exc_info=True,
                          extra={'information': {'error': str(e), 'file_path': file_path}})
            raise Error(AWS_CONNECTION_ISSUE)

    @staticmethod
    def retrieve_property_note_records(cnx, property_id, user_id, entity_type=None, entity_id=None):
        """
        Fetches the property note records from the database
        :param cnx: The MySQL connection object
        :param property_id: The id of the property
        :param user_id: The internal id of a user in our system
        :param entity_type: Optional filter by entity type
        :param entity_id: Optional filter by entity id
        :return: python list of tuples
        """
        logging.info(START_OF_METHOD)
        try:
            cursor = cnx.cursor()

            # Build dynamic query based on filters
            query = FETCH_PROPERTY_NOTES
            params = [property_id, user_id]

            if entity_type is not None:
                query += " AND entity_type = %s"
                params.append(entity_type)

            if entity_id is not None:
                query += " AND entity_id = %s"
                params.append(entity_id)

            query += " ORDER BY created_at DESC;"

            cursor.execute(query, params)
            results = cursor.fetchall()
            cursor.close()
            logging.info(END_OF_METHOD)
            return results
        except Exception as e:
            logging.error('An issue occurred retrieving property note records from the database',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INTERNAL_SERVICE_ERROR)

    def obtain_connection(self):
        try:
            cnx = self.pool.get_connection()
            return cnx
        except Exception as e:
            logging.error('An issue occurred acquiring a connection to the pool',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INTERNAL_SERVICE_ERROR)
