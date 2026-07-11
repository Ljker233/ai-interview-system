import os
from typing import Optional

from app.repositories.dynamodb_client import create_dynamodb_resource


class EvaluationRepository:
    def __init__(self):
        table_name = os.getenv("EVALUATIONS_TABLE_NAME", "Evaluations")
        dynamodb = create_dynamodb_resource()
        self.table = dynamodb.Table(table_name)

    def find_by_id(self, evaluation_id: str) -> Optional[dict]:
        response = self.table.get_item(
            Key={
                "evaluation_id": evaluation_id,
            }
        )

        return response.get("Item")

    def save(self, evaluation: dict) -> dict:
        self.table.put_item(
            Item=evaluation,
            ConditionExpression="attribute_not_exists(evaluation_id)",
        )

        return evaluation

    def update_success(
        self,
        evaluation_id: str,
        score: int,
        feedback: str,
        strengths: list[str],
        improvements: list[str],
        follow_up_questions: list[str],
        model_name: str,
        evaluated_at: str,
    ) -> None:
        self.table.update_item(
            Key={
                "evaluation_id": evaluation_id,
            },
            UpdateExpression=(
                "SET #status = :status, "
                "score = :score, "
                "feedback = :feedback, "
                "strengths = :strengths, "
                "improvements = :improvements, "
                "follow_up_questions = :follow_up_questions, "
                "model_name = :model_name, "
                "evaluated_at = :evaluated_at, "
                "updated_at = :updated_at"
            ),
            ExpressionAttributeNames={
                "#status": "status",
            },
            ExpressionAttributeValues={
                ":status": "EVALUATED",
                ":score": score,
                ":feedback": feedback,
                ":strengths": strengths,
                ":improvements": improvements,
                ":follow_up_questions": follow_up_questions,
                ":model_name": model_name,
                ":evaluated_at": evaluated_at,
                ":updated_at": evaluated_at,
            },
        )

    def update_failure(
        self,
        evaluation_id: str,
        error_message: str,
        updated_at: str,
    ) -> None:
        self.table.update_item(
            Key={
                "evaluation_id": evaluation_id,
            },
            UpdateExpression=(
                "SET #status = :status, "
                "error_message = :error_message, "
                "updated_at = :updated_at"
            ),
            ExpressionAttributeNames={
                "#status": "status",
            },
            ExpressionAttributeValues={
                ":status": "FAILED",
                ":error_message": error_message,
                ":updated_at": updated_at,
            },
        )
