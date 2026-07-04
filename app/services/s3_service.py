import os

import boto3
from fastapi import UploadFile


class S3Service:
    def __init__(self):
        aws_region = os.getenv("AWS_REGION", "us-east-1")
        bucket_name = os.getenv("RESUME_BUCKET_NAME")

        if not bucket_name:
            raise ValueError("RESUME_BUCKET_NAME is not configured")

        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            "s3",
            region_name=aws_region,
        )

    def upload_resume_file(
        self,
        file: UploadFile,
        s3_key: str,
    ) -> dict:
        self.s3_client.upload_fileobj(
            Fileobj=file.file,
            Bucket=self.bucket_name,
            Key=s3_key,
            ExtraArgs={
                "ContentType": file.content_type or "application/octet-stream",
            },
        )

        return {
            "s3_bucket": self.bucket_name,
            "s3_key": s3_key,
        }

    def generate_presigned_download_url(
        self,
        s3_key: str,
        expires_in_seconds: int = 3600,
    ) -> str:
        return self.s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": self.bucket_name,
                "Key": s3_key,
            },
            ExpiresIn=expires_in_seconds,
        )
