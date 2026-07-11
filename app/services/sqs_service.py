import json
import os

import boto3


class SQSService:
    def __init__(self):
        aws_region = os.getenv("AWS_REGION", "us-east-1")

        self.sqs_client = boto3.client(
            "sqs",
            region_name=aws_region,
        )

        self.question_generation_queue_url = os.getenv(
            "QUESTION_GENERATION_QUEUE_URL"
        )

        self.answer_evaluation_queue_url = os.getenv(
            "ANSWER_EVALUATION_QUEUE_URL"
        )

    def send_question_generation_job(self, interview_id: str) -> None:
        if not self.question_generation_queue_url:
            raise ValueError("QUESTION_GENERATION_QUEUE_URL is not configured")

        message_body = {
            "job_type": "GENERATE_INTERVIEW_QUESTIONS",
            "interview_id": interview_id,
            "schema_version": "1.0",
        }

        self.sqs_client.send_message(
            QueueUrl=self.question_generation_queue_url,
            MessageBody=json.dumps(message_body),
        )

    def send_answer_evaluation_job(self, answer_id: str) -> None:
        if not self.answer_evaluation_queue_url:
            raise ValueError("ANSWER_EVALUATION_QUEUE_URL is not configured")

        message_body = {
            "job_type": "EVALUATE_ANSWER",
            "answer_id": answer_id,
            "schema_version": "1.0",
        }

        self.sqs_client.send_message(
            QueueUrl=self.answer_evaluation_queue_url,
            MessageBody=json.dumps(message_body),
        )

    def receive_question_generation_messages(self) -> list[dict]:
        if not self.question_generation_queue_url:
            raise ValueError("QUESTION_GENERATION_QUEUE_URL is not configured")

        response = self.sqs_client.receive_message(
            QueueUrl=self.question_generation_queue_url,
            MaxNumberOfMessages=5,
            WaitTimeSeconds=10,
            VisibilityTimeout=30,
        )

        return response.get("Messages", [])

    def delete_question_generation_message(self, receipt_handle: str) -> None:
        if not self.question_generation_queue_url:
            raise ValueError("QUESTION_GENERATION_QUEUE_URL is not configured")

        self.sqs_client.delete_message(
            QueueUrl=self.question_generation_queue_url,
            ReceiptHandle=receipt_handle,
        )

    def receive_answer_evaluation_messages(self) -> list[dict]:
        if not self.answer_evaluation_queue_url:
            raise ValueError("ANSWER_EVALUATION_QUEUE_URL is not configured")

        response = self.sqs_client.receive_message(
            QueueUrl=self.answer_evaluation_queue_url,
            MaxNumberOfMessages=5,
            WaitTimeSeconds=10,
            VisibilityTimeout=30,
        )

        return response.get("Messages", [])

    def delete_answer_evaluation_message(self, receipt_handle: str) -> None:
        if not self.answer_evaluation_queue_url:
            raise ValueError("ANSWER_EVALUATION_QUEUE_URL is not configured")

        self.sqs_client.delete_message(
            QueueUrl=self.answer_evaluation_queue_url,
            ReceiptHandle=receipt_handle,
        )
