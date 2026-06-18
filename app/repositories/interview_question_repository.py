import os
from typing import Dict, List

from boto3.dynamodb.conditions import Key

from app.repositories.dynamodb_client import create_dynamodb_resource


class InterviewQuestionRepository:
    def __init__(self):
        table_name = os.getenv("INTERVIEW_QUESTIONS_TABLE_NAME", "InterviewQuestions")
        dynamodb = create_dynamodb_resource()
        self.table = dynamodb.Table(table_name)
        self.interview_questions_index_name = "interview_id-order-index"

    def save_many(self, questions: List[Dict]) -> List[Dict]:
        with self.table.batch_writer() as batch:
            for question in questions:
                batch.put_item(Item=question)

        return questions

    def find_by_interview_id(self, interview_id: str) -> List[Dict]:
        response = self.table.query(
            IndexName=self.interview_questions_index_name,
            KeyConditionExpression=Key("interview_id").eq(interview_id),
            ScanIndexForward=True,
        )
        return response.get("Items", [])
