import os

# Define AWS_REGION as a constant
AWS_REGION = "us-east-1"

class S3Sync:
    def sync_folder_to_s3(self, folder, aws_bucket_url):
        # Remove --profile parameter
        command = f"aws s3 sync {folder} {aws_bucket_url} --region {AWS_REGION}"
        print(f"Executing: {command}")  # Add logging
        os.system(command)

    def sync_folder_from_s3(self, folder, aws_bucket_url):
        # Remove --profile parameter
        command = f"aws s3 sync {aws_bucket_url} {folder} --region {AWS_REGION}"
        print(f"Executing: {command}")  # Add logging
        os.system(command)