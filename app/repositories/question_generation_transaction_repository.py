import os

import boto3
from boto3.dynamodb.types import TypeSerializer


class QuestionGenerationTransactionRepository:
    """
    Repository for atomic question generation writes.

    It writes generated questions and updates the interview status in one
    DynamoDB transaction.

    This prevents partial writes like:
        - questions saved successfully
        - interview status update failed

    Transaction result:
        - all writes succeed
        - or no writes are applied
    """

    def __init__(self):
        aws_region = os.getenv("AWS_REGION", "us-east-1")

        self.interviews_table_name = os.getenv("INTERVIEWS_TABLE_NAME", "Interviews")
        self.questions_table_name = os.getenv(
            "INTERVIEW_QUESTIONS_TABLE_NAME",
            "InterviewQuestions",
        )

        self.dynamodb_client = boto3.client(
            "dynamodb",
            region_name=aws_region,
        )

        self.serializer = TypeSerializer()

    def save_questions_and_mark_interview_ready(
        self,
        interview_id: str,
        questions: list[dict],
        updated_at: str,
    ) -> None:
        """
        Atomically:
        1. Put all generated questions into InterviewQuestions table.
        2. Update interview status to READY.

        Important:
        DynamoDB transactions support up to 25 actions.
        Since one action is used to update the interview status,
        this method supports at most 24 questions.
        """
        if len(questions) > 24:
            raise ValueError("DynamoDB transaction can save at most 24 questions here")

        transact_items = []

        for question in questions:
            transact_items.append(
                {
                    "Put": {
                        "TableName": self.questions_table_name,
                        "Item": self._serialize_item(question),
                        "ConditionExpression": "attribute_not_exists(question_id)",
                    }
                }
            )

        transact_items.append(
            {
                "Update": {
                    "TableName": self.interviews_table_name,
                    "Key": self._serialize_item(
                        {
                            "interview_id": interview_id,
                        }
                    ),
                    "UpdateExpression": "SET #status = :ready, updated_at = :updated_at",
                    "ConditionExpression": "#status = :generating",
                    "ExpressionAttributeNames": {
                        "#status": "status",
                    },
                    "ExpressionAttributeValues": {
                        ":ready": self.serializer.serialize("READY"),
                        ":generating": self.serializer.serialize("QUESTION_GENERATING"),
                        ":updated_at": self.serializer.serialize(updated_at),
                    },
                }
            }
        )

        self.dynamodb_client.transact_write_items(
            TransactItems=transact_items,
        )

    def _serialize_item(self, item: dict) -> dict:
        return {
            key: self.serializer.serialize(value)
            for key, value in item.items()
        }
