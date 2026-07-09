import os
from typing import Optional

from app.repositories.dynamodb_client import create_dynamodb_resource


class AnswerRepository:
    def __init__(self):
        table_name = os.getenv("ANSWERS_TABLE_NAME", "Answers")
        dynamodb = create_dynamodb_resource()
        self.table = dynamodb.Table(table_name)

    def find_by_id(self, answer_id: str) -> Optional[dict]:
        response = self.table.get_item(Key={"answer_id": answer_id})
        return response.get("Item")
