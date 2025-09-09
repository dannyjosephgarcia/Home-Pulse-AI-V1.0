import boto3
import logging
from common.logging.error.error import Error
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error_messages import AWS_CONNECTION_ISSUE


class SagemakerClient:
    def __init__(self, aws_access_key_id, aws_secret_access_key, region_name):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self.client = self.initialize_sagemaker_runtime_client()

    def initialize_sagemaker_runtime_client(self):
        """
        Creates a client to access S3
        :return: A boto3 Client that connects to s3
        """
        logging.info(START_OF_METHOD)
        try:
            client = boto3.Session().client(service_name='sagemaker-runtime',
                                            aws_access_key_id=self.aws_access_key_id,
                                            aws_secret_access_key=self.aws_secret_access_key,
                                            region_name=self.region_name)
            logging.info(END_OF_METHOD)
            return client
        except Exception as e:
            logging.error('An issue occurred attempting to connect to S3',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(AWS_CONNECTION_ISSUE)
