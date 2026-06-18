import os

import boto3


def create_dynamodb_resource():
    aws_region = os.getenv("AWS_REGION", "us-east-1")
    endpoint_url = os.getenv("DYNAMODB_ENDPOINT_URL")

    if endpoint_url:
        return boto3.resource(
            "dynamodb",
            region_name=aws_region,
            endpoint_url=endpoint_url,
            aws_access_key_id="dummy",
            aws_secret_access_key="dummy",
        )

    return boto3.resource(
        "dynamodb",
        region_name=aws_region,
    )
