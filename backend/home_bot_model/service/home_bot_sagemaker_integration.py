import json
import logging
import os
from typing import Dict, List, Optional, Union

import boto3
import sagemaker
from sagemaker.huggingface import HuggingFaceModel
from sagemaker.serverless import ServerlessInferenceConfig

logger = logging.getLogger(__name__)


class HomeBotSagemakerIntegration:
    """
    SageMaker integration for deploying and managing HomeBot LLM endpoints.
    Supports both FLAN-T5 (legacy) and Llama 3.1 8B Instruct models.
    """

    def __init__(self, role, session):
        """
        Initialize SageMaker integration.

        Args:
            role (str): AWS IAM role ARN for SageMaker
            session (sagemaker.Session): SageMaker session instance
        """
        self.role = role
        self.session = session
        logger.info("HomeBotSagemakerIntegration initialized")

    def deploy_mistral_llm_to_sagemaker_instance(self, hub, serverless_config):
        """
        [LEGACY] Deploys FLAN-T5-large LLM to SageMaker.

        NOTE: This method is deprecated. Use deploy_llama_model() for new deployments.

        :param hub: python dict, model configurations
        :param serverless_config: python dict, serverless configurations for cost management
        :return: SageMaker predictor instance
        """
        logger.warning("Using legacy FLAN-T5 deployment. Consider upgrading to Llama 3.1")

        hugging_face_model = HuggingFaceModel(
            sagemaker_session=self.session,
            role=self.role,
            env=hub,
            model_data='s3://home-pulse-ai-model-data/flan-t5-large.tar.gz',
            transformers_version="4.26.0",
            pytorch_version="1.13.1",
            py_version="py39",
        )
        predictor = hugging_face_model.deploy(
            initial_instance_count=1,
            instance_type='ml.g4dn.xlarge',
            endpoint_name="homebot-llm-v1"
        )
        logger.info("FLAN-T5 model deployed to endpoint: homebot-llm-v1")
        return predictor

    def deploy_llama_model(
        self,
        model_id: str = 'meta-llama/Meta-Llama-3.1-8B-Instruct',
        model_s3_path: Optional[str] = None,
        instance_type: str = 'ml.g5.2xlarge',
        endpoint_name: str = 'homebot-llama-v1',
        serverless: bool = False,
        serverless_config: Optional[Dict] = None,
        hf_token: Optional[str] = None
    ):
        """
        Deploy Llama 3.1 8B Instruct model to SageMaker.

        Args:
            model_id (str): HuggingFace model ID (e.g., 'meta-llama/Meta-Llama-3.1-8B-Instruct')
                Used when model_s3_path is None. Requires hf_token for gated models.
            model_s3_path (str): Optional S3 path to model tarball. If provided, uses custom model.
            instance_type (str): SageMaker instance type
                Recommended:
                - ml.g5.2xlarge (24GB GPU, $1.69/hr) - Best performance
                - ml.g5.xlarge (24GB GPU, $1.41/hr) - Good balance
                - ml.g4dn.2xlarge (16GB GPU, $1.05/hr) - Budget option (may OOM)
            endpoint_name (str): Name for the SageMaker endpoint
            serverless (bool): Use serverless inference (experimental)
            serverless_config (Dict): Serverless config if serverless=True
                Example: {"memory_size_in_mb": 6144, "max_concurrency": 1}
            hf_token (str): HuggingFace API token for accessing gated models

        Returns:
            Predictor: SageMaker predictor instance

        Raises:
            Exception: If deployment fails
        """
        logger.info(f"Deploying Llama 3.1 8B Instruct to SageMaker")
        logger.info(f"Instance type: {instance_type}")
        logger.info(f"Endpoint name: {endpoint_name}")

        try:
            # Build environment variables
            env = {
                'HF_TASK': 'text-generation',
                'MAX_INPUT_LENGTH': '2048',
                'MAX_TOTAL_TOKENS': '4096',
            }

            # Add HuggingFace token if provided (required for gated models)
            if hf_token:
                env['HUGGING_FACE_HUB_TOKEN'] = hf_token
                logger.info("Using HuggingFace token for model access")

            # Create HuggingFace Model
            if model_s3_path:
                # Use custom model from S3 tarball
                logger.info(f"Using custom model from: {model_s3_path}")
                hugging_face_model = HuggingFaceModel(
                    model_data=model_s3_path,
                    role=self.role,
                    sagemaker_session=self.session,
                    transformers_version="4.49.0",  # Llama 3.1 requires >= 4.43.0
                    pytorch_version="2.6.0",
                    py_version="py312",
                    env=env
                )
            else:
                # Use model directly from HuggingFace Hub
                logger.info(f"Using HuggingFace Hub model: {model_id}")
                env['HF_MODEL_ID'] = model_id
                hugging_face_model = HuggingFaceModel(
                    role=self.role,
                    sagemaker_session=self.session,
                    transformers_version="4.49.0",  # Llama 3.1 requires >= 4.43.0
                    pytorch_version="2.6.0",
                    py_version="py312",
                    env=env
                )

            # Deploy based on configuration
            if serverless:
                logger.info("Deploying as serverless endpoint")

                if serverless_config is None:
                    serverless_config = {
                        "memory_size_in_mb": 6144,  # 6GB minimum for Llama 3.1 8B
                        "max_concurrency": 1
                    }

                inference_config = ServerlessInferenceConfig(
                    memory_size_in_mb=serverless_config["memory_size_in_mb"],
                    max_concurrency=serverless_config["max_concurrency"]
                )

                predictor = hugging_face_model.deploy(
                    serverless_inference_config=inference_config,
                    endpoint_name=endpoint_name
                )
            else:
                logger.info("Deploying as dedicated instance endpoint")

                predictor = hugging_face_model.deploy(
                    initial_instance_count=1,
                    instance_type=instance_type,
                    endpoint_name=endpoint_name
                )

            logger.info(f"✓ Llama 3.1 model deployed successfully to: {endpoint_name}")
            return predictor

        except Exception as e:
            logger.error(f"Failed to deploy Llama model: {e}", exc_info=True)
            raise

    def generate_response(
        self,
        predictor,
        user_message: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 50
    ) -> Dict:
        """
        Generate response from Llama 3.1 model using chat format.

        Args:
            predictor: SageMaker predictor instance
            user_message (str): User's input message
            system_prompt (str): System prompt to set assistant persona
            conversation_history (List[Dict]): Previous conversation messages
                Format: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
            max_tokens (int): Maximum tokens to generate
            temperature (float): Sampling temperature (0.0-1.0)
            top_p (float): Nucleus sampling probability
            top_k (int): Top-k sampling parameter

        Returns:
            Dict: Generated response with metadata
                {
                    "generated_text": str,
                    "full_output": str,
                    "input_length": int,
                    "output_length": int
                }

        Example:
            >>> response = integration.generate_response(
            ...     predictor=predictor,
            ...     user_message="How long do dishwashers typically last?",
            ...     system_prompt="You are a professional property manager assistant.",
            ...     max_tokens=300
            ... )
            >>> print(response["generated_text"])
        """
        logger.info(f"Generating response for message: {user_message[:100]}...")

        try:
            # Build messages list for chat template
            messages = []

            # Add system prompt if provided
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })

            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)

            # Add current user message
            messages.append({
                "role": "user",
                "content": user_message
            })

            # Prepare payload
            payload = {
                "messages": messages,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": temperature,
                    "top_p": top_p,
                    "top_k": top_k,
                    "do_sample": True if temperature > 0 else False,
                    "repetition_penalty": 1.1
                }
            }

            logger.debug(f"Payload: {json.dumps(payload, indent=2)}")

            # Invoke endpoint
            response = predictor.predict(payload)

            logger.info("Response generated successfully")
            return response

        except Exception as e:
            logger.error(f"Failed to generate response: {e}", exc_info=True)
            raise

    def generate_response_legacy(
        self,
        predictor,
        prompt: str,
        max_length: int = 256,
        temperature: float = 0.7
    ) -> str:
        """
        [LEGACY] Generate response from FLAN-T5 model.

        NOTE: Use generate_response() for Llama 3.1 deployments.

        Args:
            predictor: SageMaker predictor instance
            prompt (str): Input prompt
            max_length (int): Maximum output length
            temperature (float): Sampling temperature

        Returns:
            str: Generated text
        """
        logger.warning("Using legacy FLAN-T5 generation method")

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": max_length,
                "temperature": temperature
            }
        }

        response = predictor.predict(payload)
        return response[0]["generated_text"]

    def delete_endpoint(self, endpoint_name: str) -> bool:
        """
        Delete a SageMaker endpoint and its configuration.

        Args:
            endpoint_name (str): Name of endpoint to delete

        Returns:
            bool: True if deletion successful

        Raises:
            Exception: If deletion fails
        """
        logger.info(f"Deleting endpoint: {endpoint_name}")

        try:
            sagemaker_client = self.session.boto_session.client('sagemaker')

            # Delete endpoint
            sagemaker_client.delete_endpoint(EndpointName=endpoint_name)
            logger.info(f"Endpoint {endpoint_name} deleted")

            # Delete endpoint config
            try:
                sagemaker_client.delete_endpoint_config(
                    EndpointConfigName=endpoint_name
                )
                logger.info(f"Endpoint config {endpoint_name} deleted")
            except Exception as e:
                logger.warning(f"Could not delete endpoint config: {e}")

            return True

        except Exception as e:
            logger.error(f"Failed to delete endpoint: {e}", exc_info=True)
            raise

    def list_endpoints(self) -> List[Dict]:
        """
        List all active SageMaker endpoints.

        Returns:
            List[Dict]: List of endpoint information
        """
        logger.info("Listing SageMaker endpoints")

        try:
            sagemaker_client = self.session.boto_session.client('sagemaker')
            response = sagemaker_client.list_endpoints(
                SortBy='CreationTime',
                SortOrder='Descending',
                MaxResults=50
            )

            endpoints = response.get('Endpoints', [])
            logger.info(f"Found {len(endpoints)} endpoints")

            return endpoints

        except Exception as e:
            logger.error(f"Failed to list endpoints: {e}", exc_info=True)
            raise

    def wait_for_endpoint_ready(self, endpoint_name: str, max_wait_seconds: int = 180) -> bool:
        """
        Wait for endpoint to be fully ready for inference (worker loaded).

        Args:
            endpoint_name (str): Name of the endpoint
            max_wait_seconds (int): Maximum time to wait in seconds

        Returns:
            bool: True if ready, False if timeout

        Raises:
            Exception: If endpoint check fails
        """
        import time

        logger.info(f"Waiting for endpoint {endpoint_name} to be fully ready...")
        logger.info(f"This may take 2-3 minutes for large models like Llama 3.1...")

        sagemaker_client = self.session.boto_session.client('sagemaker')
        runtime_client = self.session.boto_session.client('sagemaker-runtime')

        start_time = time.time()
        retry_count = 0

        while time.time() - start_time < max_wait_seconds:
            try:
                # Check endpoint status
                response = sagemaker_client.describe_endpoint(EndpointName=endpoint_name)
                status = response['EndpointStatus']

                if status != 'InService':
                    logger.info(f"Endpoint status: {status}. Waiting...")
                    time.sleep(10)
                    continue

                # Try a health check inference
                logger.info("Endpoint is InService. Testing worker readiness...")
                try:
                    test_payload = {
                        "inputs": "Hello",
                        "parameters": {"max_new_tokens": 5}
                    }
                    runtime_client.invoke_endpoint(
                        EndpointName=endpoint_name,
                        ContentType='application/json',
                        Body=json.dumps(test_payload)
                    )
                    logger.info(f"✓ Endpoint {endpoint_name} is fully ready!")
                    return True

                except Exception as e:
                    error_msg = str(e)
                    if "worker pid is not available" in error_msg or "ModelError" in error_msg:
                        retry_count += 1
                        elapsed = int(time.time() - start_time)
                        logger.info(f"Worker not ready yet (attempt {retry_count}, {elapsed}s elapsed). Waiting...")
                        time.sleep(10)
                    else:
                        # Different error, re-raise
                        raise

            except Exception as e:
                if "worker pid is not available" not in str(e):
                    logger.error(f"Error checking endpoint: {e}")
                    raise
                time.sleep(10)

        logger.warning(f"Timeout waiting for endpoint after {max_wait_seconds}s")
        return False


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Load AWS credentials
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_SAGEMAKER_ROLE = os.getenv('AWS_SAGEMAKER_ROLE')

    if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SAGEMAKER_ROLE]):
        logger.error("Missing required AWS credentials!")
        logger.error("Set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_SAGEMAKER_ROLE")
        exit(1)

    # Initialize SageMaker session
    CLIENT = boto3.client(
        'sagemaker-runtime',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name='us-east-1'
    )
    SAGEMAKER_SESSION = sagemaker.Session(
        sagemaker_runtime_client=CLIENT,
        default_bucket='home-pulse-ai-model-data'
    )

    # Initialize integration
    integration = HomeBotSagemakerIntegration(AWS_SAGEMAKER_ROLE, SAGEMAKER_SESSION)

    # Choose deployment type
    DEPLOY_LLAMA = True  # Set to False to deploy legacy FLAN-T5

    if DEPLOY_LLAMA:
        logger.info("=" * 70)
        logger.info("Deploying Llama 3.1 8B Instruct")
        logger.info("=" * 70)

        # Option 1: Deploy from HuggingFace Hub (recommended, simpler)
        # Requires HuggingFace token for gated models: https://huggingface.co/settings/tokens
        HF_TOKEN = os.getenv('HUGGING_FACE_TOKEN')

        predictor = integration.deploy_llama_model(
            model_id='meta-llama/Meta-Llama-3.1-8B-Instruct',  # Direct from HF Hub
            hf_token=HF_TOKEN,  # Required for Llama (gated model)
            instance_type='ml.g5.2xlarge',  # Recommended for Llama 3.1 8B
            endpoint_name='homebot-llama-v1',
            serverless=False
        )

        # Option 2: Deploy from custom S3 tarball (if you have pre-packaged model)
        # predictor = integration.deploy_llama_model(
        #     model_s3_path='s3://home-pulse-ai-model-data/llama-3.1-8b-instruct.tar.gz',
        #     instance_type='ml.g5.2xlarge',
        #     endpoint_name='homebot-llama-v1',
        #     serverless=False
        # )

        # Wait for endpoint to be fully ready before testing
        logger.info("\nWaiting for endpoint to be fully ready...")
        if not integration.wait_for_endpoint_ready(predictor.endpoint_name, max_wait_seconds=300):
            logger.error("Endpoint did not become ready in time. Skipping test.")
        else:
            logger.info("\nTesting Llama 3.1 endpoint...")

            # Test generation
            system_prompt = """You are HomeBot, a professional property management assistant.
You help property managers with appliance maintenance, lifecycle predictions, and cost analysis.
Provide clear, concise, and practical advice."""

            test_response = integration.generate_response(
                predictor=predictor,
                user_message="How long do dishwashers typically last, and when should I replace them?",
                system_prompt=system_prompt,
                max_tokens=300,
                temperature=0.7
            )

            logger.info("\n" + "=" * 70)
            logger.info("Test Response:")
            logger.info("=" * 70)
            logger.info(test_response.get("generated_text", "No response"))

    else:
        logger.info("=" * 70)
        logger.info("Deploying FLAN-T5 (Legacy)")
        logger.info("=" * 70)

        HUB = {
            "HF_TASK": "text2text-generation",
            "HF_MODEL_ID": "google/flan-t5-large"
        }
        SERVERLESS_CONFIG = {
            "memory_size_in_mb": 3072,
            "max_concurrency": 1
        }

        predictor = integration.deploy_mistral_llm_to_sagemaker_instance(
            HUB,
            SERVERLESS_CONFIG
        )

        # Test legacy generation
        test_response = integration.generate_response_legacy(
            predictor=predictor,
            prompt="How long do dishwashers last?",
            max_length=256
        )

        logger.info("\n" + "=" * 70)
        logger.info("Test Response:")
        logger.info("=" * 70)
        logger.info(test_response)

    logger.info("\n" + "=" * 70)
    logger.info("Deployment Complete!")
    logger.info("=" * 70)
    logger.info(f"Endpoint Name: {predictor.endpoint_name}")
    logger.info("\nTo delete this endpoint later, run:")
    logger.info(f"  integration.delete_endpoint('{predictor.endpoint_name}')")
    logger.info("=" * 70)
