from datetime import datetime, timezone

from app.repositories.answer_repository import AnswerRepository
from app.repositories.evaluation_repository import EvaluationRepository
from app.repositories.interview_question_repository import (
    InterviewQuestionRepository,
)
from app.repositories.interview_repository import InterviewRepository
from app.services.ai_service import AIService


class EvaluationService:
    def __init__(
        self,
        answer_repository: AnswerRepository,
        evaluation_repository: EvaluationRepository,
        interview_question_repository: InterviewQuestionRepository,
        interview_repository: InterviewRepository,
        ai_service: AIService,
    ):
        self.answer_repository = answer_repository
        self.evaluation_repository = evaluation_repository
        self.interview_question_repository = interview_question_repository
        self.interview_repository = interview_repository
        self.ai_service = ai_service

    def evaluate_answer(self, answer_id: str) -> dict:
        answer = self.answer_repository.find_by_id(answer_id)

        if answer is None:
            raise ValueError("Answer not found")

        evaluation_id = self._build_evaluation_id(answer_id)

        existing_evaluation = self.evaluation_repository.find_by_id(
            evaluation_id
        )

        if existing_evaluation and existing_evaluation.get("status") == "EVALUATED":
            return {
                "evaluation_id": evaluation_id,
                "answer_id": answer_id,
                "status": "EVALUATED",
                "message": "Answer already evaluated",
            }

        current_answer_status = answer.get("status")

        if current_answer_status == "EVALUATED":
            return {
                "evaluation_id": evaluation_id,
                "answer_id": answer_id,
                "status": "EVALUATED",
                "message": "Answer already evaluated",
            }

        if current_answer_status not in {
            "SUBMITTED",
            "EVALUATION_FAILED",
            "EVALUATING",
        }:
            raise ValueError(
                f"Answer cannot be evaluated from status {current_answer_status}"
            )

        now = self._now_iso()

        self.answer_repository.update_status(
            answer_id=answer_id,
            status="EVALUATING",
            updated_at=now,
        )

        self._create_or_get_evaluation(
            evaluation_id=evaluation_id,
            answer=answer,
            created_at=now,
        )

        interview_id = answer.get("interview_id")
        question_id = answer.get("question_id")

        question = self.interview_question_repository.find_by_id(question_id)
        if question is None:
            self._mark_evaluation_failed(
                evaluation_id=evaluation_id,
                answer_id=answer_id,
                error_message="Question not found",
            )
            raise ValueError("Question not found")

        interview = self.interview_repository.find_by_id(interview_id)
        if interview is None:
            self._mark_evaluation_failed(
                evaluation_id=evaluation_id,
                answer_id=answer_id,
                error_message="Interview not found",
            )
            raise ValueError("Interview not found")

        try:
            result = self.ai_service.evaluate_answer(
                question=question,
                answer=answer,
                interview=interview,
            )

            evaluated_at = self._now_iso()

            self.evaluation_repository.update_success(
                evaluation_id=evaluation_id,
                score=result.get("score", 0),
                feedback=result.get("feedback", ""),
                strengths=result.get("strengths", []),
                improvements=result.get("improvements", []),
                follow_up_questions=result.get("follow_up_questions", []),
                model_name=result.get("model_name", "mock-llm"),
                evaluated_at=evaluated_at,
            )

            self.answer_repository.update_status(
                answer_id=answer_id,
                status="EVALUATED",
                updated_at=evaluated_at,
            )

            self._maybe_update_interview_status(
                interview_id=interview_id,
                updated_at=evaluated_at,
            )

            return {
                "evaluation_id": evaluation_id,
                "answer_id": answer_id,
                "status": "EVALUATED",
                "message": "Answer evaluated successfully",
            }

        except Exception as error:
            self._mark_evaluation_failed(
                evaluation_id=evaluation_id,
                answer_id=answer_id,
                error_message=str(error),
            )
            raise

    def _create_or_get_evaluation(
        self,
        evaluation_id: str,
        answer: dict,
        created_at: str,
    ) -> dict:
        existing_evaluation = self.evaluation_repository.find_by_id(
            evaluation_id
        )

        if existing_evaluation:
            return existing_evaluation

        evaluation = {
            "evaluation_id": evaluation_id,
            "answer_id": answer.get("answer_id"),
            "interview_id": answer.get("interview_id"),
            "question_id": answer.get("question_id"),
            "user_id": answer.get("user_id"),
            "status": "EVALUATING",
            "prompt_version": "answer_evaluation_v1",
            "created_at": created_at,
            "updated_at": created_at,
        }

        return self.evaluation_repository.save(evaluation)

    def _mark_evaluation_failed(
        self,
        evaluation_id: str,
        answer_id: str,
        error_message: str,
    ) -> None:
        now = self._now_iso()

        self.evaluation_repository.update_failure(
            evaluation_id=evaluation_id,
            error_message=error_message,
            updated_at=now,
        )

        self.answer_repository.update_status(
            answer_id=answer_id,
            status="EVALUATION_FAILED",
            updated_at=now,
        )

    def _maybe_update_interview_status(
        self,
        interview_id: str,
        updated_at: str,
    ) -> None:
        questions = self.interview_question_repository.find_by_interview_id(
            interview_id
        )

        if not questions:
            return

        for question in questions:
            if question.get("status") != "ANSWERED":
                return

            question_id = question.get("question_id")
            answer_id = self._build_answer_id(question_id)

            answer = self.answer_repository.find_by_id(answer_id)

            if answer is None or answer.get("status") != "EVALUATED":
                self.interview_repository.update_status(
                    interview_id=interview_id,
                    status="EVALUATING",
                    updated_at=updated_at,
                )
                return

        self.interview_repository.update_status(
            interview_id=interview_id,
            status="INTERVIEW_EVALUATED",
            updated_at=updated_at,
        )

    def _build_answer_id(self, question_id: str) -> str:
        return f"ans_{question_id}"

    def _build_evaluation_id(self, answer_id: str) -> str:
        return f"eval_{answer_id}"

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()
    
    def get_evaluation_for_question(
    self,
    interview_id: str,
    question_id: str,
    ) -> dict:
        answer_id = self._build_answer_id(question_id)
        evaluation_id = self._build_evaluation_id(answer_id)

        evaluation = self.evaluation_repository.find_by_id(evaluation_id)

        if evaluation is None:
            raise ValueError("Evaluation not ready yet")

        if evaluation.get("interview_id") != interview_id:
            raise ValueError("Evaluation does not belong to this interview")

        return evaluation
