import json
import os
from typing import Any

import boto3


class SQSService:
    def __init__(self):
        aws_region = os.getenv("AWS_REGION", "us-east-1")
        queue_url = os.getenv("QUESTION_GENERATION_QUEUE_URL")

        if not queue_url:
            raise ValueError("QUESTION_GENERATION_QUEUE_URL is not configured")

        self.queue_url = queue_url
        self.sqs_client = boto3.client(
            "sqs",
            region_name=aws_region,
        )

    def send_question_generation_job(self, interview_id: str) -> None:
        """
        Producer side.

        Called by InterviewService after creating an interview.
        The message only contains interview_id because DynamoDB is the source of truth.
        """
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

    def receive_messages(self) -> list[dict[str, Any]]:
        """
        Consumer side.

        Receive at most one message at a time.
        WaitTimeSeconds=10 enables long polling.
        """
        response = self.sqs_client.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10,
            MessageAttributeNames=["All"],
        )

        return response.get("Messages", [])

    def delete_message(self, receipt_handle: str) -> None:
        """
        Delete the message only after processing succeeds.
        """
        self.sqs_client.delete_message(
            QueueUrl=self.queue_url,
            ReceiptHandle=receipt_handle,
        )
