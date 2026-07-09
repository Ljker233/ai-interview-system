import os

import boto3
from boto3.dynamodb.types import TypeSerializer


class AnswerTransactionRepository:
    def __init__(self):
        aws_region = os.getenv("AWS_REGION", "us-east-1")
        self.dynamodb_client = boto3.client("dynamodb", region_name=aws_region)
        self.serializer = TypeSerializer()
        self.answers_table_name = os.getenv("ANSWERS_TABLE_NAME", "Answers")
        self.questions_table_name = os.getenv(
            "INTERVIEW_QUESTIONS_TABLE_NAME",
            "InterviewQuestions",
        )

    def submit_answer_transaction(
        self,
        answer_item: dict,
        question_id: str,
        interview_id: str,
        submitted_at: str,
    ) -> None:
        """
        Atomically:
        1. Create one Answer item.
        2. Update the Question status from CREATED to ANSWERED.
        """
        self.dynamodb_client.transact_write_items(
            TransactItems=[
                {
                    "Put": {
                        "TableName": self.answers_table_name,
                        "Item": self._to_dynamodb_item(answer_item),
                        "ConditionExpression": "attribute_not_exists(answer_id)",
                    }
                },
                {
                    "Update": {
                        "TableName": self.questions_table_name,
                        "Key": {
                            "question_id": {"S": question_id}
                        },
                        "UpdateExpression": (
                            "SET #status = :answered, "
                            "answered_at = :answered_at, "
                            "updated_at = :updated_at"
                        ),
                        "ConditionExpression": (
                            "#status = :created AND interview_id = :interview_id"
                        ),
                        "ExpressionAttributeNames": {
                            "#status": "status",
                        },
                        "ExpressionAttributeValues": {
                            ":answered": {"S": "ANSWERED"},
                            ":created": {"S": "CREATED"},
                            ":interview_id": {"S": interview_id},
                            ":answered_at": {"S": submitted_at},
                            ":updated_at": {"S": submitted_at},
                        },
                    }
                },
            ]
        )

    def _to_dynamodb_item(self, item: dict) -> dict:
        return {
            key: self.serializer.serialize(value)
            for key, value in item.items()
        }
