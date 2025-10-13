"""
Llama 3.1 8B Instruct Model Download and Packaging Script

This script downloads the Llama 3.1 8B Instruct model from HuggingFace,
packages it in SageMaker-compatible format, and creates a .tar.gz archive
ready for upload to S3.

Prerequisites:
    - HuggingFace account with Llama 3.1 access approved
    - HuggingFace token with read permissions
    - At least 30GB free disk space
    - Python packages: transformers, torch, huggingface_hub

Usage:
    python scripts/download_llama_3_1.py --hf-token YOUR_TOKEN --output-dir ./llama_model
"""

import argparse
import json
import os
import shutil
import tarfile
from pathlib import Path

import torch
from huggingface_hub import login, snapshot_download
from transformers import AutoModelForCausalLM, AutoTokenizer


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Download and package Llama 3.1 8B Instruct for SageMaker"
    )
    parser.add_argument(
        "--hf-token",
        type=str,
        required=True,
        help="HuggingFace access token (required for gated Llama models)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./llama_3_1_8b_instruct",
        help="Directory to save the model (default: ./llama_3_1_8b_instruct)"
    )
    parser.add_argument(
        "--model-id",
        type=str,
        default="meta-llama/Meta-Llama-3.1-8B-Instruct",
        help="HuggingFace model ID (default: meta-llama/Meta-Llama-3.1-8B-Instruct)"
    )
    parser.add_argument(
        "--use-fp16",
        action="store_true",
        help="Save model in FP16 precision (reduces size from ~32GB to ~16GB)"
    )
    parser.add_argument(
        "--skip-model-download",
        action="store_true",
        help="Skip downloading model if already exists in output directory"
    )
    return parser.parse_args()


def authenticate_huggingface(token):
    """
    Authenticate with HuggingFace Hub.

    Args:
        token (str): HuggingFace access token

    Raises:
        Exception: If authentication fails
    """
    print("\n" + "="*70)
    print("STEP 1: Authenticating with HuggingFace Hub")
    print("="*70)

    try:
        login(token=token)
        print("✓ Successfully authenticated with HuggingFace")
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        print("\nPlease ensure:")
        print("1. Your HuggingFace token is valid")
        print("2. You have accepted the Llama 3.1 license at:")
        print("   https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct")
        raise


def download_model_files(model_id, output_dir, skip_download=False):
    """
    Download model files from HuggingFace Hub using snapshot_download.

    Args:
        model_id (str): HuggingFace model identifier
        output_dir (str): Directory to save downloaded files
        skip_download (bool): Skip download if directory exists

    Returns:
        Path: Path to downloaded model directory
    """
    print("\n" + "="*70)
    print("STEP 2: Downloading Model Files")
    print("="*70)

    model_path = Path(output_dir) / "model"

    if skip_download and model_path.exists():
        print(f"✓ Model directory already exists at {model_path}, skipping download")
        return model_path

    print(f"Downloading {model_id}...")
    print("This may take 15-30 minutes depending on your connection speed.")
    print(f"Model will be saved to: {model_path}")

    try:
        # Download all model files
        downloaded_path = snapshot_download(
            repo_id=model_id,
            local_dir=str(model_path),
            local_dir_use_symlinks=False,
            resume_download=True
        )
        print(f"✓ Model files downloaded successfully to {downloaded_path}")
        return Path(downloaded_path)
    except Exception as e:
        print(f"✗ Download failed: {e}")
        raise


def optimize_model_precision(model_path, use_fp16=True):
    """
    Optionally convert model to FP16 to reduce size.

    Args:
        model_path (Path): Path to model directory
        use_fp16 (bool): Whether to convert to FP16
    """
    if not use_fp16:
        print("\nSkipping FP16 conversion (using original precision)")
        return

    print("\n" + "="*70)
    print("STEP 3: Converting Model to FP16")
    print("="*70)
    print("This reduces model size from ~32GB to ~16GB")

    try:
        print("Loading model...")
        model = AutoModelForCausalLM.from_pretrained(
            str(model_path),
            torch_dtype=torch.float16,
            device_map="cpu",
            low_cpu_mem_usage=True
        )

        print("Saving FP16 model...")
        model.save_pretrained(str(model_path), safe_serialization=True)

        print("✓ Model converted to FP16 successfully")

        # Clean up
        del model
        torch.cuda.empty_cache()

    except Exception as e:
        print(f"✗ FP16 conversion failed: {e}")
        print("Continuing with original model files...")


def create_inference_script(code_dir):
    """
    Create custom inference.py script for SageMaker.

    Args:
        code_dir (Path): Directory to save inference script
    """
    print("\n" + "="*70)
    print("STEP 4: Creating Custom Inference Script")
    print("="*70)

    inference_code = '''"""
Custom SageMaker inference script for Llama 3.1 8B Instruct.
Handles model loading, tokenization, and generation with chat templates.
"""

import json
import logging
import os
from typing import Dict, List, Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig

logger = logging.getLogger(__name__)


def model_fn(model_dir: str):
    """
    Load the model and tokenizer for inference.

    Args:
        model_dir (str): Path to model directory

    Returns:
        tuple: (model, tokenizer)
    """
    logger.info(f"Loading model from {model_dir}")

    try:
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_dir)

        # Ensure pad token is set
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        # Load model with FP16 precision for GPU efficiency
        model = AutoModelForCausalLM.from_pretrained(
            model_dir,
            torch_dtype=torch.float16,
            device_map="auto",
            low_cpu_mem_usage=True
        )

        model.eval()

        logger.info("Model and tokenizer loaded successfully")
        return model, tokenizer

    except Exception as e:
        logger.error(f"Error loading model: {e}", exc_info=True)
        raise


def format_chat_messages(
    messages: List[Dict[str, str]],
    tokenizer
) -> str:
    """
    Format messages using Llama 3.1 chat template.

    Args:
        messages (List[Dict]): List of message dicts with 'role' and 'content'
        tokenizer: HuggingFace tokenizer

    Returns:
        str: Formatted prompt
    """
    # Llama 3.1 uses the apply_chat_template method
    formatted_prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    return formatted_prompt


def predict_fn(input_data: Dict, model_and_tokenizer: tuple) -> Dict:
    """
    Make predictions using the loaded model.

    Args:
        input_data (Dict): Input data with keys:
            - messages (List[Dict]): Chat messages (preferred)
            - OR inputs (str): Raw text prompt
            - parameters (Dict): Generation parameters (optional)
        model_and_tokenizer (tuple): (model, tokenizer) from model_fn

    Returns:
        Dict: Generated response
    """
    model, tokenizer = model_and_tokenizer

    try:
        # Extract input data
        messages = input_data.get("messages")
        raw_input = input_data.get("inputs")
        parameters = input_data.get("parameters", {})

        # Format prompt
        if messages:
            # Chat format (preferred)
            prompt = format_chat_messages(messages, tokenizer)
        elif raw_input:
            # Raw text format (fallback)
            prompt = raw_input
        else:
            raise ValueError("Must provide either 'messages' or 'inputs' in request")

        # Tokenize
        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=parameters.get("max_input_length", 2048)
        ).to(model.device)

        # Generation parameters with defaults
        generation_config = GenerationConfig(
            max_new_tokens=parameters.get("max_new_tokens", 512),
            temperature=parameters.get("temperature", 0.7),
            top_p=parameters.get("top_p", 0.9),
            top_k=parameters.get("top_k", 50),
            do_sample=parameters.get("do_sample", True),
            repetition_penalty=parameters.get("repetition_penalty", 1.1),
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

        # Generate
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                generation_config=generation_config
            )

        # Decode output
        generated_text = tokenizer.decode(
            outputs[0],
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True
        )

        # Extract only the generated response (remove input prompt)
        response_text = generated_text[len(prompt):].strip()

        return {
            "generated_text": response_text,
            "full_output": generated_text,
            "input_length": len(inputs["input_ids"][0]),
            "output_length": len(outputs[0])
        }

    except Exception as e:
        logger.error(f"Error during prediction: {e}", exc_info=True)
        return {"error": str(e)}


def input_fn(request_body: bytes, content_type: str = "application/json") -> Dict:
    """
    Deserialize input data.

    Args:
        request_body (bytes): Request body
        content_type (str): Content type

    Returns:
        Dict: Deserialized input data
    """
    if content_type == "application/json":
        return json.loads(request_body)
    else:
        raise ValueError(f"Unsupported content type: {content_type}")


def output_fn(prediction: Dict, accept: str = "application/json") -> bytes:
    """
    Serialize prediction output.

    Args:
        prediction (Dict): Prediction result
        accept (str): Accept header

    Returns:
        bytes: Serialized output
    """
    if accept == "application/json":
        return json.dumps(prediction)
    else:
        raise ValueError(f"Unsupported accept type: {accept}")
'''

    code_dir.mkdir(parents=True, exist_ok=True)
    inference_path = code_dir / "inference.py"

    with open(inference_path, "w", encoding="utf-8") as f:
        f.write(inference_code)

    print(f"✓ Created inference script at {inference_path}")


def create_requirements_file(code_dir):
    """
    Create requirements.txt for SageMaker container.

    Args:
        code_dir (Path): Directory to save requirements file
    """
    requirements = """transformers==4.37.2
torch==2.1.2
accelerate==0.26.1
sentencepiece==0.1.99
"""

    requirements_path = code_dir / "requirements.txt"
    with open(requirements_path, "w", encoding="utf-8") as f:
        f.write(requirements)

    print(f"✓ Created requirements.txt at {requirements_path}")


def create_tarball(output_dir):
    """
    Create .tar.gz archive of the model for SageMaker deployment.

    Args:
        output_dir (str): Directory containing model files

    Returns:
        str: Path to created tarball
    """
    print("\n" + "="*70)
    print("STEP 5: Creating TAR.GZ Archive")
    print("="*70)

    output_path = Path(output_dir)
    tarball_path = output_path.parent / "llama-3.1-8b-instruct.tar.gz"

    print(f"Creating archive at: {tarball_path}")
    print("This may take several minutes...")

    try:
        with tarfile.open(tarball_path, "w:gz") as tar:
            # Add model directory
            tar.add(
                output_path / "model",
                arcname=".",
                recursive=True
            )

            # Add code directory if it exists
            code_dir = output_path / "code"
            if code_dir.exists():
                tar.add(
                    code_dir,
                    arcname="code",
                    recursive=True
                )

        # Get file size
        size_mb = tarball_path.stat().st_size / (1024 * 1024)
        print(f"✓ Archive created successfully: {tarball_path}")
        print(f"  Size: {size_mb:.2f} MB")

        return str(tarball_path)

    except Exception as e:
        print(f"✗ Failed to create archive: {e}")
        raise


def print_next_steps(tarball_path, output_dir):
    """
    Print instructions for next steps.

    Args:
        tarball_path (str): Path to created tarball
        output_dir (str): Directory containing model files
    """
    print("\n" + "="*70)
    print("SUCCESS! Model Package Ready for Upload")
    print("="*70)

    print(f"\nModel archive created at: {tarball_path}")

    print("\n" + "-"*70)
    print("NEXT STEPS:")
    print("-"*70)

    print("\n1. Upload the model to S3:")
    print(f"   python scripts/upload_model_to_s3.py \\")
    print(f"       --file {tarball_path} \\")
    print(f"       --bucket home-pulse-ai-model-data \\")
    print(f"       --key llama-3.1-8b-instruct.tar.gz")

    print("\n2. Deploy to SageMaker:")
    print("   python backend/home_bot_model/service/home_bot_sagemaker_integration.py")

    print("\n3. Test the endpoint:")
    print("   See docs/llama_deployment_guide.md for testing instructions")

    print("\n" + "-"*70)
    print("IMPORTANT NOTES:")
    print("-"*70)
    print("- Archive size: Make sure you have enough S3 storage")
    print("- Recommended instance: ml.g5.2xlarge (24GB GPU, ~$1.69/hour)")
    print("- Estimated deployment time: 5-10 minutes")
    print("- Model uses ~16GB GPU memory (FP16)")

    print("\n" + "="*70)


def main():
    """Main execution function."""
    args = parse_args()

    print("\n" + "="*70)
    print("Llama 3.1 8B Instruct - SageMaker Package Creator")
    print("="*70)
    print(f"\nModel ID: {args.model_id}")
    print(f"Output Directory: {args.output_dir}")
    print(f"FP16 Optimization: {'Enabled' if args.use_fp16 else 'Disabled'}")

    try:
        # Step 1: Authenticate
        authenticate_huggingface(args.hf_token)

        # Step 2: Download model
        model_path = download_model_files(
            args.model_id,
            args.output_dir,
            args.skip_model_download
        )

        # Step 3: Optimize precision (optional)
        if args.use_fp16:
            optimize_model_precision(model_path, use_fp16=True)

        # Step 4: Create inference script
        code_dir = Path(args.output_dir) / "code"
        create_inference_script(code_dir)
        create_requirements_file(code_dir)

        # Step 5: Create tarball
        tarball_path = create_tarball(args.output_dir)

        # Print next steps
        print_next_steps(tarball_path, args.output_dir)

    except Exception as e:
        print(f"\n✗ Process failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())