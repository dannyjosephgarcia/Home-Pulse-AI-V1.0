"""
S3 Model Upload Helper Script

Uploads the packaged Llama 3.1 model tarball to S3 for SageMaker deployment.

Prerequisites:
    - AWS credentials configured (environment variables or AWS CLI)
    - S3 bucket exists and you have write permissions
    - Model tarball created by download_llama_3_1.py

Usage:
    python scripts/upload_model_to_s3.py \\
        --file ./llama-3.1-8b-instruct.tar.gz \\
        --bucket home-pulse-ai-model-data \\
        --key llama-3.1-8b-instruct.tar.gz
"""

import argparse
import os
import sys
from pathlib import Path

import boto3
from botocore.exceptions import ClientError, NoCredentialsError


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Upload model tarball to S3 for SageMaker deployment"
    )
    parser.add_argument(
        "--file",
        type=str,
        required=True,
        help="Path to model tarball (.tar.gz file)"
    )
    parser.add_argument(
        "--bucket",
        type=str,
        required=True,
        help="S3 bucket name (e.g., home-pulse-ai-model-data)"
    )
    parser.add_argument(
        "--key",
        type=str,
        required=True,
        help="S3 object key/path (e.g., llama-3.1-8b-instruct.tar.gz)"
    )
    parser.add_argument(
        "--region",
        type=str,
        default="us-east-1",
        help="AWS region (default: us-east-1)"
    )
    parser.add_argument(
        "--aws-profile",
        type=str,
        default=None,
        help="AWS profile name (optional, uses default if not specified)"
    )
    return parser.parse_args()


def validate_file(file_path):
    """
    Validate that the file exists and is readable.

    Args:
        file_path (str): Path to file

    Returns:
        tuple: (bool, int, str) - (valid, size_bytes, error_message)
    """
    path = Path(file_path)

    if not path.exists():
        return False, 0, f"File not found: {file_path}"

    if not path.is_file():
        return False, 0, f"Path is not a file: {file_path}"

    if not file_path.endswith('.tar.gz'):
        return False, 0, "File must be a .tar.gz archive"

    try:
        size = path.stat().st_size
        if size == 0:
            return False, 0, "File is empty"

        return True, size, None
    except Exception as e:
        return False, 0, f"Error reading file: {e}"


def format_size(bytes_size):
    """
    Format bytes to human-readable size.

    Args:
        bytes_size (int): Size in bytes

    Returns:
        str: Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"


def create_s3_client(region, profile=None):
    """
    Create and configure S3 client.

    Args:
        region (str): AWS region
        profile (str): AWS profile name (optional)

    Returns:
        boto3.client: S3 client

    Raises:
        NoCredentialsError: If AWS credentials are not configured
    """
    print("\n" + "="*70)
    print("STEP 1: Configuring AWS S3 Client")
    print("="*70)

    try:
        if profile:
            print(f"Using AWS profile: {profile}")
            session = boto3.Session(profile_name=profile, region_name=region)
            s3_client = session.client('s3')
        else:
            print("Using default AWS credentials")
            s3_client = boto3.client('s3', region_name=region)

        # Test credentials
        s3_client.list_buckets()
        print("✓ AWS credentials validated successfully")

        return s3_client

    except NoCredentialsError:
        print("\n✗ AWS credentials not found!")
        print("\nPlease configure credentials using one of these methods:")
        print("1. Environment variables:")
        print("   export AWS_ACCESS_KEY_ID=your_key")
        print("   export AWS_SECRET_ACCESS_KEY=your_secret")
        print("\n2. AWS CLI configuration:")
        print("   aws configure")
        print("\n3. AWS credentials file:")
        print("   ~/.aws/credentials")
        raise
    except ClientError as e:
        print(f"\n✗ AWS credential error: {e}")
        raise


def verify_bucket_access(s3_client, bucket_name):
    """
    Verify that the S3 bucket exists and is accessible.

    Args:
        s3_client: boto3 S3 client
        bucket_name (str): S3 bucket name

    Returns:
        bool: True if bucket is accessible

    Raises:
        ClientError: If bucket doesn't exist or access denied
    """
    print("\n" + "="*70)
    print("STEP 2: Verifying S3 Bucket Access")
    print("="*70)

    try:
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"✓ Bucket '{bucket_name}' exists and is accessible")
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']

        if error_code == '404':
            print(f"\n✗ Bucket '{bucket_name}' does not exist")
            print("\nCreate the bucket first:")
            print(f"  aws s3 mb s3://{bucket_name}")
        elif error_code == '403':
            print(f"\n✗ Access denied to bucket '{bucket_name}'")
            print("\nCheck your IAM permissions:")
            print("  - s3:GetBucket*")
            print("  - s3:PutObject")
        else:
            print(f"\n✗ Error accessing bucket: {e}")

        raise


def upload_with_progress(s3_client, file_path, bucket_name, key, file_size):
    """
    Upload file to S3 with progress tracking.

    Args:
        s3_client: boto3 S3 client
        file_path (str): Path to file
        bucket_name (str): S3 bucket name
        key (str): S3 object key
        file_size (int): File size in bytes

    Returns:
        str: S3 URI of uploaded file

    Raises:
        ClientError: If upload fails
    """
    print("\n" + "="*70)
    print("STEP 3: Uploading Model to S3")
    print("="*70)
    print(f"Source: {file_path}")
    print(f"Destination: s3://{bucket_name}/{key}")
    print(f"Size: {format_size(file_size)}")
    print("\nUploading... This may take several minutes for large files.")

    # Progress callback
    class ProgressPercentage:
        def __init__(self, filename, file_size):
            self._filename = filename
            self._size = file_size
            self._seen_so_far = 0
            self._last_percent = 0

        def __call__(self, bytes_amount):
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100

            # Print progress every 5%
            if int(percentage) >= self._last_percent + 5:
                self._last_percent = int(percentage)
                print(f"  Progress: {percentage:.1f}% ({format_size(self._seen_so_far)} / {format_size(self._size)})")

    try:
        progress = ProgressPercentage(file_path, file_size)

        s3_client.upload_file(
            file_path,
            bucket_name,
            key,
            Callback=progress,
            ExtraArgs={
                'ContentType': 'application/gzip',
                'Metadata': {
                    'model-type': 'llama-3.1-8b-instruct',
                    'framework': 'pytorch',
                    'purpose': 'sagemaker-deployment'
                }
            }
        )

        s3_uri = f"s3://{bucket_name}/{key}"
        print(f"\n✓ Upload completed successfully!")
        print(f"  S3 URI: {s3_uri}")

        return s3_uri

    except ClientError as e:
        print(f"\n✗ Upload failed: {e}")
        raise


def verify_upload(s3_client, bucket_name, key, expected_size):
    """
    Verify that the uploaded file exists and has correct size.

    Args:
        s3_client: boto3 S3 client
        bucket_name (str): S3 bucket name
        key (str): S3 object key
        expected_size (int): Expected file size in bytes

    Returns:
        bool: True if verification passes
    """
    print("\n" + "="*70)
    print("STEP 4: Verifying Upload")
    print("="*70)

    try:
        response = s3_client.head_object(Bucket=bucket_name, Key=key)
        actual_size = response['ContentLength']

        print(f"Expected size: {format_size(expected_size)}")
        print(f"Actual size:   {format_size(actual_size)}")

        if actual_size == expected_size:
            print("✓ File size matches - upload verified!")
            return True
        else:
            print("✗ File size mismatch - upload may be corrupted!")
            return False

    except ClientError as e:
        print(f"✗ Verification failed: {e}")
        return False


def print_next_steps(s3_uri):
    """
    Print instructions for next steps.

    Args:
        s3_uri (str): S3 URI of uploaded model
    """
    print("\n" + "="*70)
    print("SUCCESS! Model Ready for Deployment")
    print("="*70)

    print(f"\nModel uploaded to: {s3_uri}")

    print("\n" + "-"*70)
    print("NEXT STEPS:")
    print("-"*70)

    print("\n1. Deploy to SageMaker:")
    print("   Update the model_data parameter in:")
    print("   backend/home_bot_model/service/home_bot_sagemaker_integration.py")
    print(f"   model_data='{s3_uri}'")

    print("\n2. Run deployment script:")
    print("   python backend/home_bot_model/service/home_bot_sagemaker_integration.py")

    print("\n3. Test the endpoint:")
    print("   Use the SagemakerClient to invoke predictions")

    print("\n" + "-"*70)
    print("INSTANCE RECOMMENDATIONS:")
    print("-"*70)
    print("For Llama 3.1 8B Instruct (FP16, ~16GB):")
    print("  - ml.g5.2xlarge  - 24GB GPU, $1.69/hr (RECOMMENDED)")
    print("  - ml.g5.xlarge   - 24GB GPU, $1.41/hr (shared, slower)")
    print("  - ml.g4dn.2xlarge - 16GB GPU, $1.05/hr (tight fit, may OOM)")

    print("\n" + "="*70)


def main():
    """Main execution function."""
    args = parse_args()

    print("\n" + "="*70)
    print("S3 Model Upload - SageMaker Deployment")
    print("="*70)
    print(f"\nFile: {args.file}")
    print(f"Bucket: {args.bucket}")
    print(f"Key: {args.key}")
    print(f"Region: {args.region}")

    try:
        # Validate file
        print("\n" + "="*70)
        print("STEP 0: Validating File")
        print("="*70)

        valid, file_size, error = validate_file(args.file)
        if not valid:
            print(f"✗ File validation failed: {error}")
            return 1

        print(f"✓ File valid: {args.file}")
        print(f"  Size: {format_size(file_size)}")

        # Create S3 client
        s3_client = create_s3_client(args.region, args.aws_profile)

        # Verify bucket access
        verify_bucket_access(s3_client, args.bucket)

        # Upload with progress
        s3_uri = upload_with_progress(
            s3_client,
            args.file,
            args.bucket,
            args.key,
            file_size
        )

        # Verify upload
        verified = verify_upload(s3_client, args.bucket, args.key, file_size)
        if not verified:
            print("\n⚠ Warning: Upload verification failed!")
            print("You may want to re-upload the file.")

        # Print next steps
        print_next_steps(s3_uri)

        return 0

    except Exception as e:
        print(f"\n✗ Upload process failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
