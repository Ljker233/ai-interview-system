from app.repositories.answer_repository import AnswerRepository
from app.repositories.evaluation_repository import EvaluationRepository
from app.repositories.interview_question_repository import (
    InterviewQuestionRepository,
)
from app.repositories.interview_repository import InterviewRepository


class InterviewQueryService:
    def __init__(
        self,
        interview_repository: InterviewRepository,
        interview_question_repository: InterviewQuestionRepository,
        answer_repository: AnswerRepository,
        evaluation_repository: EvaluationRepository,
    ):
        self.interview_repository = interview_repository
        self.interview_question_repository = interview_question_repository
        self.answer_repository = answer_repository
        self.evaluation_repository = evaluation_repository

    def list_interviews_by_user(self, user_id: str) -> dict:
        if not user_id or not user_id.strip():
            raise ValueError("user_id is required")

        interviews = self.interview_repository.list_by_user_id(user_id)

        return {
            "user_id": user_id,
            "interviews": interviews,
        }

    def get_interview_details(self, interview_id: str) -> dict:
        if not interview_id or not interview_id.strip():
            raise ValueError("interview_id is required")

        interview = self.interview_repository.find_by_id(interview_id)

        if interview is None:
            raise ValueError("Interview not found")

        questions = self.interview_question_repository.find_by_interview_id(
            interview_id
        )

        question_details = []

        for question in questions:
            question_id = question.get("question_id")

            answer = None
            evaluation = None

            if question_id:
                answer = self.answer_repository.find_by_question_id(question_id)

            if answer is not None:
                answer_id = answer.get("answer_id")
                evaluation = self.evaluation_repository.find_by_answer_id(
                    answer_id
                )

            question_details.append(
                {
                    "question": question,
                    "answer": answer,
                    "evaluation": evaluation,
                }
            )

        return {
            "interview": interview,
            "questions": question_details,
        }
