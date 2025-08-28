import logging
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error_messages import INTERNAL_SERVICE_ERROR, AWS_CONNECTION_ISSUE
from common.logging.error.error import Error
from backend.db.model.query.sql_statements import SELECT_PROPERTY_IMAGE_URL


class PropertyImageRetrievalService:
    def __init__(self, hp_ai_connection_pool, s3_client, bucket_name):
        self.pool = hp_ai_connection_pool.pool
        self.s3_client = s3_client.initialize_s3_client()
        self.bucket_name = bucket_name

    def fetch_and_sign_property_image_url(self, user_id, property_id):
        """
        Retrieves the property image URL from S3 based on user_id and property_id
        :param user_id:
        :param property_id:
        :return:
        """
        logging.info(START_OF_METHOD)
        cnx = self.obtain_connection()
        image_key = self.retrieve_property_image_key(
            cnx=cnx,
            user_id=user_id,
            property_id=property_id)
        cnx.close()
        signed_url = self.sign_image_url(
            image_key=image_key)
        logging.info(END_OF_METHOD)
        return {'signedURL': signed_url}

    def sign_image_url(self, image_key):
        """
        Returns a signed url for the frontend to upload a photo to
        :param image_key: The key of the image in S3
        :return: python str, the signed URL
        """
        logging.info(START_OF_METHOD)
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": image_key},
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
    def retrieve_property_image_key(cnx, user_id, property_id):
        """
        Fetches the property image key stored inside our property_images table
        :param cnx: The MySQL connection object
        :param user_id: The internal id of a user in our system
        :param property_id: The internal id of a property in our system
        :return: python str, the URL to sign
        """
        logging.info(START_OF_METHOD)
        try:
            cursor = cnx.cursor()
            cursor.execute(SELECT_PROPERTY_IMAGE_URL, [user_id, property_id])
            result = cursor.fetchall()
            image_url = result[0][0]
            cursor.close()
            logging.info(END_OF_METHOD)
            return image_url
        except Exception as e:
            logging.error('An issue occurred retrieving the property image URL from the database',
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