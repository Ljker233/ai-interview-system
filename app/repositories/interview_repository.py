import os
from typing import Optional

from boto3.dynamodb.conditions import Key

from app.repositories.dynamodb_client import create_dynamodb_resource


class InterviewRepository:
    def __init__(self):
        table_name = os.getenv("INTERVIEWS_TABLE_NAME", "Interviews")
        dynamodb = create_dynamodb_resource()
        self.table = dynamodb.Table(table_name)

    def save(self, interview: dict) -> dict:
        self.table.put_item(Item=interview)
        return interview

    def find_by_id(self, interview_id: str) -> Optional[dict]:
        response = self.table.get_item(
            Key={
                "interview_id": interview_id,
            }
        )

        return response.get("Item")

    def update_status(
        self,
        interview_id: str,
        status: str,
        updated_at: str,
    ) -> None:
        self.table.update_item(
            Key={
                "interview_id": interview_id,
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

    def list_by_user_id(self, user_id: str) -> list[dict]:
        """
        Requires GSI on Interviews table:

        GSI name: user_id-created_at-index
        Partition key: user_id
        Sort key: created_at
        """
        items = []
        exclusive_start_key = None

        while True:
            query_kwargs = {
                "IndexName": "user_id-created_at-index",
                "KeyConditionExpression": Key("user_id").eq(user_id),
                "ScanIndexForward": False,
            }

            if exclusive_start_key:
                query_kwargs["ExclusiveStartKey"] = exclusive_start_key

            response = self.table.query(**query_kwargs)
            items.extend(response.get("Items", []))

            exclusive_start_key = response.get("LastEvaluatedKey")
            if not exclusive_start_key:
                break

        return items
