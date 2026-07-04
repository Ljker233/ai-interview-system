import os
from typing import Optional

from app.repositories.dynamodb_client import create_dynamodb_resource


class UserRepository:
    def __init__(self):
        table_name = os.getenv("USERS_TABLE_NAME", "Users")
        dynamodb = create_dynamodb_resource()
        self.table = dynamodb.Table(table_name)

    def save(self, user: dict) -> dict:
        self.table.put_item(Item=user)
        return user

    def find_by_id(self, user_id: str) -> Optional[dict]:
        response = self.table.get_item(
            Key={
                "user_id": user_id,
            }
        )

        return response.get("Item")

    def update_current_resume(
        self,
        user_id: str,
        current_resume: dict,
        updated_at: str,
    ) -> None:
        self.table.update_item(
            Key={
                "user_id": user_id,
            },
            UpdateExpression=(
                "SET current_resume = :current_resume, "
                "updated_at = :updated_at"
            ),
            ExpressionAttributeValues={
                ":current_resume": current_resume,
                ":updated_at": updated_at,
            },
        )
