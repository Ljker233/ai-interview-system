from datetime import datetime, timezone

from app.repositories.answer_repository import AnswerRepository
from app.repositories.answer_transaction_repository import (
    AnswerTransactionRepository,
)
from app.repositories.interview_question_repository import (
    InterviewQuestionRepository,
)
from app.repositories.interview_repository import InterviewRepository


class AnswerService:
    def __init__(
        self,
        answer_repository: AnswerRepository,
        answer_transaction_repository: AnswerTransactionRepository,
        interview_repository: InterviewRepository,
        interview_question_repository: InterviewQuestionRepository,
    ):
        self.answer_repository = answer_repository
        self.answer_transaction_repository = answer_transaction_repository
        self.interview_repository = interview_repository
        self.interview_question_repository = interview_question_repository

    def submit_answer(
        self,
        interview_id: str,
        question_id: str,
        answer_text: str,
    ) -> dict:
        if not answer_text or not answer_text.strip():
            raise ValueError("Answer cannot be empty")

        interview = self.interview_repository.find_by_id(interview_id)
        if interview is None:
            raise ValueError("Interview not found")

        question = self.interview_question_repository.find_by_id(question_id)
        if question is None:
            raise ValueError("Question not found")

        if question.get("interview_id") != interview_id:
            raise ValueError("Question does not belong to this interview")

        if question.get("status") != "CREATED":
            raise ValueError("Question has already been answered")

        submitted_at = self._now_iso()
        answer_id = self._build_answer_id(question_id)

        existing_answer = self.answer_repository.find_by_id(answer_id)
        if existing_answer is not None:
            raise ValueError("Answer already exists for this question")

        # Do not ask the client to pass user_id here.
        # The answer inherits user_id from the interview.
        answer_item = {
            "answer_id": answer_id,
            "interview_id": interview_id,
            "question_id": question_id,
            "user_id": interview.get("user_id", ""),
            "answer_text": answer_text.strip(),
            "status": "SUBMITTED",
            "created_at": submitted_at,
            "updated_at": submitted_at,
        }

        self.answer_transaction_repository.submit_answer_transaction(
            answer_item=answer_item,
            question_id=question_id,
            interview_id=interview_id,
            submitted_at=submitted_at,
        )

        self._update_interview_status_after_answer(
            interview_id=interview_id,
            answered_question_id=question_id,
            updated_at=submitted_at,
        )

        return {
            "answer_id": answer_id,
            "interview_id": interview_id,
            "question_id": question_id,
            "status": "SUBMITTED",
            "message": "Answer submitted successfully",
        }

    def _update_interview_status_after_answer(
        self,
        interview_id: str,
        answered_question_id: str,
        updated_at: str,
    ) -> None:
        questions = self.interview_question_repository.find_by_interview_id(
            interview_id
        )

        if not questions:
            return

        # GSI query may be eventually consistent. Treat the current question as answered.
        all_answered = True
        for question in questions:
            if question.get("question_id") == answered_question_id:
                continue

            if question.get("status") != "ANSWERED":
                all_answered = False
                break

        next_status = "ANSWERS_SUBMITTED" if all_answered else "IN_PROGRESS"

        self.interview_repository.update_status(
            interview_id=interview_id,
            status=next_status,
            updated_at=updated_at,
        )

    def _build_answer_id(self, question_id: str) -> str:
        return f"ans_{question_id}"

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()
