from datetime import datetime, timezone
from typing import List
from uuid import uuid4

from app.models.interview import CreateInterviewRequest, InterviewType
from app.repositories.interview_repository import InterviewRepository
from app.repositories.interview_question_repository import InterviewQuestionRepository


class InterviewService:
    def __init__(
        self,
        interview_repository: InterviewRepository,
        question_repository: InterviewQuestionRepository,
    ):
        self.interview_repository = interview_repository
        self.question_repository = question_repository

    def create_interview(self, request: CreateInterviewRequest) -> dict:
        self._validate_interview_types(request.interview_types)

        interview_id = str(uuid4())
        created_at = datetime.now(timezone.utc).isoformat()

        interview = {
            "interview_id": interview_id,
            "user_id": request.user_id,
            "interview_types": [
                interview_type.value for interview_type in request.interview_types
            ],
            "target_role": request.target_role,
            "difficulty": request.difficulty,
            "status": "CREATED",
            "created_at": created_at,
        }

        questions = self._generate_question_items(
            interview_id=interview_id,
            interview_types=request.interview_types,
            target_role=request.target_role,
            difficulty=request.difficulty,
            created_at=created_at,
        )

        self.interview_repository.save(interview)
        self.question_repository.save_many(questions)

        return {
            **interview,
            "questions": questions,
        }

    def get_interview(self, interview_id: str) -> dict:
        interview = self.interview_repository.find_by_id(interview_id)

        if interview is None:
            raise ValueError("Interview not found")

        questions = self.question_repository.find_by_interview_id(interview_id)

        return {
            **interview,
            "questions": questions,
        }

    def get_interviews_by_user(self, user_id: str) -> List[dict]:
        interviews = self.interview_repository.find_by_user_id(user_id)

        result = []
        for interview in interviews:
            interview_id = interview["interview_id"]
            questions = self.question_repository.find_by_interview_id(interview_id)

            result.append(
                {
                    **interview,
                    "questions": questions,
                }
            )

        return result

    def _validate_interview_types(self, interview_types: List[InterviewType]) -> None:
        if len(interview_types) != len(set(interview_types)):
            raise ValueError("Duplicate interview types are not allowed")

    def _generate_question_items(
        self,
        interview_id: str,
        interview_types: List[InterviewType],
        target_role: str,
        difficulty: str,
        created_at: str,
    ) -> List[dict]:
        questions = []

        for index, interview_type in enumerate(interview_types, start=1):
            question_text = self._generate_question_text(
                interview_type=interview_type,
                target_role=target_role,
                difficulty=difficulty,
            )

            question = {
                "question_id": str(uuid4()),
                "interview_id": interview_id,
                "type": interview_type.value,
                "question": question_text,
                "question_order": index,
                "status": "CREATED",
                "created_at": created_at,
            }

            questions.append(question)

        return questions

    def _generate_question_text(
        self,
        interview_type: InterviewType,
        target_role: str,
        difficulty: str,
    ) -> str:
        if interview_type == InterviewType.coding:
            return (
                f"You are interviewing for a {target_role} role. "
                f"Solve this {difficulty} coding problem: "
                "Given an array of integers, return the two numbers that add up to a target."
            )

        if interview_type == InterviewType.behavioral:
            return (
                f"Tell me about a time you solved a difficult problem "
                f"as a {target_role}."
            )

        if interview_type == InterviewType.system_design:
            return (
                f"Design a scalable AI interview practice platform. "
                f"Focus on APIs, database, async workers, and reliability. "
                f"Difficulty: {difficulty}."
            )

        return f"Tell me about your experience as a {target_role}."
