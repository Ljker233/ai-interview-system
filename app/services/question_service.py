import json
import time
from datetime import datetime, timezone

from app.repositories.interview_question_repository import InterviewQuestionRepository
from app.repositories.interview_repository import InterviewRepository
from app.repositories.question_generation_transaction_repository import (
    QuestionGenerationTransactionRepository,
)
from app.services.ai_service import AIService
from app.services.sqs_service import SQSService


class QuestionService:
    def __init__(
        self,
        interview_repository=None,
        interview_question_repository=None,
        sqs_service=None,
        ai_service=None,
        transaction_repository=None,
    ):
        self.interview_repository = interview_repository or InterviewRepository()
        self.interview_question_repository = (
            interview_question_repository or InterviewQuestionRepository()
        )
        self.sqs_service = sqs_service or SQSService()
        self.ai_service = ai_service or AIService()
        self.transaction_repository = (
            transaction_repository or QuestionGenerationTransactionRepository()
        )

    def listen_for_question_generation_messages(self) -> None:
        """
        Keep polling SQS and process question generation jobs.

        Local run:
            python -c "from app.services.question_service import QuestionService; QuestionService().listen_for_question_generation_messages()"

        Better run:
            python -m app.workers.question_generation_listener
        """
        print("Question generation listener started...")

        while True:
            messages = self.sqs_service.receive_messages()

            if not messages:
                print("No messages. Waiting...")
                time.sleep(3)
                continue

            for message in messages:
                try:
                    print(f"Received message: {message.get('MessageId')}")

                    self.process_sqs_message(message)

                    self.sqs_service.delete_message(
                        receipt_handle=message["ReceiptHandle"]
                    )

                    print("Message processed successfully and deleted")

                except Exception as error:
                    print("Failed to process SQS message")
                    print("Error type:", type(error).__name__)
                    print("Error message:", error)

                    # Do not delete the message when processing fails.
                    # SQS will make it visible again after visibility timeout.
                    # In production, configure DLQ to avoid infinite retries.

    def process_sqs_message(self, message: dict) -> None:
        """
        Read one SQS message, validate it, and generate questions.
        """
        body = json.loads(message["Body"])

        job_type = body.get("job_type")
        interview_id = body.get("interview_id")

        if job_type != "GENERATE_INTERVIEW_QUESTIONS":
            raise ValueError(f"Unsupported job_type: {job_type}")

        if not interview_id:
            raise ValueError("Missing interview_id in SQS message")

        print(f"Processing interview_id: {interview_id}")

        self.generate_questions_for_interview(interview_id)

    def generate_questions_for_interview(self, interview_id: str) -> None:
        """
        Main business method.

        Steps:
        1. Read interview from DynamoDB.
        2. Validate interview status.
        3. Call AIService to generate questions.
        4. Build deterministic question items.
        5. Transactionally save questions and update interview status to READY.

        Why transaction?
        If question writes succeed but status update fails, we get partial data.
        A transaction makes these writes all-or-nothing.
        """
        interview = self.interview_repository.find_by_id(interview_id)

        if interview is None:
            raise ValueError(f"Interview not found: {interview_id}")

        current_status = interview.get("status")

        if current_status == "READY":
            print(f"Interview {interview_id} is already READY. Skipping.")
            return

        if current_status != "QUESTION_GENERATING":
            raise ValueError(
                f"Interview {interview_id} is not ready for question generation. "
                f"Current status: {current_status}"
            )

        print("Calling AIService to generate questions...")
        ai_questions = self.ai_service.generate_interview_questions(interview)

        question_items = self._build_question_items(
            interview_id=interview_id,
            ai_questions=ai_questions,
        )

        now = datetime.now(timezone.utc).isoformat()

        print(
            f"Saving {len(question_items)} questions and marking interview READY "
            "in one DynamoDB transaction..."
        )

        self.transaction_repository.save_questions_and_mark_interview_ready(
            interview_id=interview_id,
            questions=question_items,
            updated_at=now,
        )

        print(f"Interview {interview_id} is now READY")

    def get_questions_for_interview(self, interview_id: str) -> list[dict]:
        """
        Return generated questions for an interview.
        Useful for GET /interviews/{interview_id}/questions later.
        """
        return self.interview_question_repository.find_by_interview_id(interview_id)

    def _build_question_items(
        self,
        interview_id: str,
        ai_questions: list[dict],
    ) -> list[dict]:
        """
        Convert AI-generated questions into DynamoDB items.

        Important:
        question_id is deterministic, not random UUID.

        Before:
            question_id = random uuid
            Retry may create duplicate questions.

        Now:
            question_id = f"{interview_id}#{question_order}"
            Retry uses the same question ids.
        """
        now = datetime.now(timezone.utc).isoformat()
        question_items = []

        for index, ai_question in enumerate(ai_questions):
            question_order = index + 1

            question_items.append(
                {
                    "question_id": f"{interview_id}#{question_order}",
                    "interview_id": interview_id,
                    "type": ai_question["type"],
                    "question": ai_question["question"],
                    "expected_signals": ai_question.get("expected_signals", []),
                    "follow_up_questions": ai_question.get("follow_up_questions", []),
                    "question_order": question_order,
                    "status": "CREATED",
                    "created_at": now,
                    "updated_at": now,
                }
            )

        return question_items
