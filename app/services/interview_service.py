from uuid import uuid4
from typing import List

from app.models.interview import CreateInterviewRequest, InterviewType
from app.repositories.interview_repository import InterviewRepository


class InterviewService:
    def __init__(self, repository: InterviewRepository):
        self.repository = repository

    def create_interview(self, request: CreateInterviewRequest) -> dict:
        interview_id = str(uuid4())

        questions = self._generate_questions(
            interview_types=request.interview_types,
            target_role=request.target_role,
            difficulty=request.difficulty
        )

        interview = {
            "interview_id": interview_id,
            "user_id": request.user_id,
            "interview_types": [interview_type.value for interview_type in request.interview_types],
            "target_role": request.target_role,
            "difficulty": request.difficulty,
            "questions": questions,
            "status": "CREATED"
        }

        return self.repository.save(interview)

    def get_interview(self, interview_id: str) -> dict:
        interview = self.repository.find_by_id(interview_id)

        if interview is None:
            raise ValueError("Interview not found")

        return interview

    def get_interviews_by_user(self, user_id: str) -> List[dict]:
        return self.repository.find_by_user_id(user_id)

    def _generate_questions(
        self,
        interview_types: List[InterviewType],
        target_role: str,
        difficulty: str
    ) -> List[dict]:
        questions = []

        for interview_type in interview_types:
            question = self._generate_question(
                interview_type=interview_type,
                target_role=target_role,
                difficulty=difficulty
            )

            questions.append({
                "type": interview_type.value,
                "question": question
            })

        return questions

    def _generate_question(
        self,
        interview_type: InterviewType,
        target_role: str,
        difficulty: str
    ) -> str:
        if interview_type == InterviewType.coding:
            return (
                f"You are interviewing for a {target_role} role. "
                f"Solve this {difficulty} coding problem: "
                f"Given an array of integers, return the two numbers that add up to a target."
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