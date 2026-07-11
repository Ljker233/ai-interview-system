import os
from typing import Optional

from app.repositories.dynamodb_client import create_dynamodb_resource


class AnswerRepository:
    def __init__(self):
        table_name = os.getenv("ANSWERS_TABLE_NAME", "Answers")
        dynamodb = create_dynamodb_resource()
        self.table = dynamodb.Table(table_name)

    def find_by_id(self, answer_id: str) -> Optional[dict]:
        response = self.table.get_item(
            Key={
                "answer_id": answer_id,
            }
        )

        return response.get("Item")

    def update_status(
        self,
        answer_id: str,
        status: str,
        updated_at: str,
    ) -> None:
        self.table.update_item(
            Key={
                "answer_id": answer_id,
            },
            UpdateExpression="SET #status = :status, updated_at = :updated_at",
            ExpressionAttributeNames={
                "#status": "status",
            },
            ExpressionAttributeValues={
                ":status": status,
                ":updated_at": updated_at,
            },
        )
