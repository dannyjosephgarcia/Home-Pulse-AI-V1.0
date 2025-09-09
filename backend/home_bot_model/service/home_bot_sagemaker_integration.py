import os

import boto3
import sagemaker
from sagemaker.huggingface import HuggingFaceModel
from sagemaker.serverless import ServerlessInferenceConfig


class HomeBotSagemakerIntegration:
    def __init__(self, role, session):
        self.role = role
        self.session = session

    def deploy_mistral_llm_to_sagemaker_instance(self, hub, serverless_config):
        """
        Deploys the LLM Wrapper for HomeBot to Sagemaker
        :param hub: python dict, model configurations
        :param serverless_config: python dict, serverless configurations for cost management
        :return:
        """
        hugging_face_model = HuggingFaceModel(
            sagemaker_session=self.session,
            role=self.role,
            env=hub,
            model_data='s3://home-pulse-ai-model-data/flan-t5-large.tar.gz',
            transformers_version="4.26.0",
            pytorch_version="1.13.1",
            py_version="py39",
        )
        predictor = hugging_face_model.deploy(initial_instance_count=1,
                                              instance_type='ml.g4dn.xlarge',
                                              endpoint_name="homebot-llm-v1")
        return predictor


if __name__ == "__main__":
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_SAGEMAKER_ROLE = os.getenv('AWS_SAGEMAKER_ROLE')
    CLIENT = boto3.client('sagemaker-runtime',
                          aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                          region_name='us-east-1')
    SAGEMAKER_SESSION = sagemaker.Session(sagemaker_runtime_client=CLIENT, default_bucket='home-pulse-ai-model-data')
    HUB = {
    "HF_TASK": "text2text-generation",
    "HF_MODEL_ID": "google/flan-t5-large"
}
    SERVERLESS_CONFIG = {
        "memory_size_in_mb": 3072,
        "max_concurrency": 1
    }
    home_bot_sagemaker_integration = HomeBotSagemakerIntegration(AWS_SAGEMAKER_ROLE, SAGEMAKER_SESSION)
    predictor = home_bot_sagemaker_integration.deploy_mistral_llm_to_sagemaker_instance(HUB, SERVERLESS_CONFIG)
