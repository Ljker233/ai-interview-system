from datetime import datetime, timezone
from typing import List
from uuid import uuid4

from app.models.interview import CreateInterviewRequest, InterviewType
from app.repositories.interview_repository import InterviewRepository
from app.services.sqs_service import SQSService


class InterviewService:
    def __init__(
        self,
        interview_repository: InterviewRepository,
        sqs_service: SQSService,
    ):
        self.interview_repository = interview_repository
        self.sqs_service = sqs_service

    def create_interview(self, request: CreateInterviewRequest) -> dict:
        self._validate_interview_types(request.interview_types)

        interview_id = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()

        interview = {
            "interview_id": interview_id,
            "user_id": request.user_id,
            "interview_types": [
                interview_type.value for interview_type in request.interview_types
            ],
            "target_role": request.target_role,
            "difficulty": request.difficulty,
            "status": "QUESTION_GENERATING",
            "created_at": now,
            "updated_at": now,
        }

        self.interview_repository.save(interview)

        self.sqs_service.send_question_generation_job(
            interview_id=interview_id
        )

        return {
            **interview,
            "message": "Interview created. Questions are being generated.",
        }

    def get_interview(self, interview_id: str) -> dict:
        interview = self.interview_repository.find_by_id(interview_id)

        if interview is None:
            raise ValueError("Interview not found")

        return interview

    def _validate_interview_types(self, interview_types: List[InterviewType]) -> None:
        if len(interview_types) != len(set(interview_types)):
            raise ValueError("Duplicate interview types are not allowed")
