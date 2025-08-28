import logging
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error import Error
from common.logging.error.error_messages import INTERNAL_SERVICE_ERROR, AWS_CONNECTION_ISSUE
from backend.db.model.query.sql_statements import INSERT_PROPERTY_IMAGE_URL


class PropertyImageInsertionService:
    def __init__(self, hp_ai_connection_pool, s3_client, bucket_name):
        self.pool = hp_ai_connection_pool.pool
        self.s3_client = s3_client.client
        self.bucket_name = bucket_name

    def insert_and_sign_property_image_url(self, user_id, property_id, file_name):
        """
        Inserts the file key into the property_images table and returns a signed URL for the frontend
        :param user_id: The internal id of a user in our system
        :param property_id: The id of a property in our system
        :param file_name: The name of the file to upload
        :return: python dict
        """
        logging.info(START_OF_METHOD)
        cnx = self.obtain_connection()
        image_key = self._construct_s3_image_key(
            user_id=user_id,
            property_id=property_id,
            file_name=file_name)
        signed_put_url = self.sign_put_image_url(
            image_key=image_key)
        put_record_status = self.insert_property_image_url(
            cnx=cnx,
            user_id=user_id,
            property_id=property_id,
            image_key=image_key)
        cnx.close()
        response = {
            'imageUrl': signed_put_url,
            'imageKey': image_key,
            'putRecordStatus': put_record_status
        }
        logging.info(END_OF_METHOD)
        return response

    def sign_put_image_url(self, image_key):
        """
        Generates a signed image URL for the frontend to upload to s3
        :param image_key: The location where the file will be stored
        :return:
        """
        logging.info(START_OF_METHOD)
        try:
            url = self.s3_client.generate_presigned_url(
                "put_object",
                Params={"Bucket": self.bucket_name,
                        "Key": image_key,
                        "ContentType": "image/jpeg"},
                ExpiresIn=600
            )
            logging.info(END_OF_METHOD)
            return url
        except Exception as e:
            logging.error('An issue occurred generating a presigned URL for S3',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(AWS_CONNECTION_ISSUE)

    @staticmethod
    def insert_property_image_url(cnx, user_id, property_id, image_key):
        """
        Function inserts the property URL into the table
        :param cnx: The MySQLConnectionPool
        :param user_id: The internal id of a user in our system
        :param property_id: The internal id of a property in our system
        :param image_key: The location of the file
        :return: python dict
        """
        logging.info(START_OF_METHOD)
        put_record_status = 200
        try:
            cursor = cnx.cursor()
            cursor.execute(INSERT_PROPERTY_IMAGE_URL, [user_id, property_id, image_key])
            cnx.commit()
            cursor.close()
            logging.info(END_OF_METHOD)
            return put_record_status
        except Exception as e:
            logging.error('There was an issue uploading the image url to the table',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INTERNAL_SERVICE_ERROR)

    @staticmethod
    def _construct_s3_image_key(user_id, property_id, file_name):
        image_key = f"users/{user_id}/properties/{property_id}/{file_name}"
        return image_key

    def obtain_connection(self):
        try:
            cnx = self.pool.get_connection()
            return cnx
        except Exception as e:
            logging.error('An issue occurred acquiring a connection to the pool',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INTERNAL_SERVICE_ERROR)