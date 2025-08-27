import logging
import os
import boto3
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD


class S3Client:
    def __init__(self, aws_access_key_id, aws_secret_access_key, region_name):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name

    def initialize_s3_client(self):
        """
        Creates a client to access S3
        :return: A boto3 Client that connects to s3
        """
        logging.info(START_OF_METHOD)
        client = boto3.Session().client(service_name='s3',
                                        aws_access_key_id=self.aws_access_key_id,
                                        aws_secret_access_key=self.aws_secret_access_key,
                                        region_name=self.region_name)
        logging.info(END_OF_METHOD)
        return client
