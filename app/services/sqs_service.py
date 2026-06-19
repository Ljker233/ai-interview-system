import json
import os

import boto3


class SQSService:
    def __init__(self):
        aws_region = os.getenv("AWS_REGION", "us-east-1")
        queue_url = os.getenv("QUESTION_GENERATION_QUEUE_URL", "https://sqs.us-east-1.amazonaws.com/557170681123/question-generation-queue")

        if not queue_url:
            raise ValueError("QUESTION_GENERATION_QUEUE_URL is not configured")

        self.queue_url = queue_url
        self.sqs_client = boto3.client(
            "sqs",
            region_name=aws_region,
        )

    def send_question_generation_job(self, interview_id: str) -> None:
        message = {
            "job_type": "GENERATE_INTERVIEW_QUESTIONS",
            "interview_id": interview_id,
            "schema_version": "1.0",
        }

        self.sqs_client.send_message(
            QueueUrl=self.queue_url,
            MessageBody=json.dumps(message),
            MessageAttributes={
                "job_type": {
                    "StringValue": "GENERATE_INTERVIEW_QUESTIONS",
                    "DataType": "String",
                }
            },
        )
