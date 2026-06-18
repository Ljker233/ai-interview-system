import os
from typing import Dict, List, Optional

from boto3.dynamodb.conditions import Key

from app.repositories.dynamodb_client import create_dynamodb_resource


class InterviewRepository:
    def __init__(self):
        table_name = os.getenv("INTERVIEWS_TABLE_NAME", "Interviews")
        dynamodb = create_dynamodb_resource()
        self.table = dynamodb.Table(table_name)
        self.user_history_index_name = "user_id-created_at-index"
        print("table_name: ", table_name)
        print("self.table: ", self.table)

    def save(self, interview: Dict) -> Dict:
        self.table.put_item(Item=interview)
        return interview

    def find_by_id(self, interview_id: str) -> Optional[Dict]:
        response = self.table.get_item(
            Key={"interview_id": interview_id}
        )
        return response.get("Item")

    def find_by_user_id(self, user_id: str) -> List[Dict]:
        response = self.table.query(
            IndexName=self.user_history_index_name,
            KeyConditionExpression=Key("user_id").eq(user_id),
            ScanIndexForward=False,
        )
        return response.get("Items", [])
