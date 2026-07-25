import os
from typing import Optional

from boto3.dynamodb.conditions import Key

from app.repositories.dynamodb_client import create_dynamodb_resource


class InterviewQuestionRepository:
    def __init__(self):
        table_name = os.getenv(
            "INTERVIEW_QUESTIONS_TABLE_NAME",
            "InterviewQuestions",
        )
        dynamodb = create_dynamodb_resource()
        self.table = dynamodb.Table(table_name)

    def save(self, question: dict) -> dict:
        self.table.put_item(Item=question)
        return question

    def save_many(self, questions: list[dict]) -> list[dict]:
        with self.table.batch_writer() as batch:
            for question in questions:
                batch.put_item(Item=question)

        return questions

    def find_by_id(self, question_id: str) -> Optional[dict]:
        response = self.table.get_item(
            Key={
                "question_id": question_id,
            }
        )

        return response.get("Item")

    def find_by_interview_id(self, interview_id: str) -> list[dict]:
        """
        Requires GSI on InterviewQuestions table:

        GSI name: interview_id-order-index
        Partition key: interview_id
        Sort key: question_order
        """
        items = []
        exclusive_start_key = None

        while True:
            query_kwargs = {
                "IndexName": "interview_id-order-index",
                "KeyConditionExpression": Key("interview_id").eq(interview_id),
                "ScanIndexForward": True,
            }

            if exclusive_start_key:
                query_kwargs["ExclusiveStartKey"] = exclusive_start_key

            response = self.table.query(**query_kwargs)
            items.extend(response.get("Items", []))

            exclusive_start_key = response.get("LastEvaluatedKey")
            if not exclusive_start_key:
                break

        return items
