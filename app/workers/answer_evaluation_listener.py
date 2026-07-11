import json
import time

from app.repositories.answer_repository import AnswerRepository
from app.repositories.evaluation_repository import EvaluationRepository
from app.repositories.interview_question_repository import (
    InterviewQuestionRepository,
)
from app.repositories.interview_repository import InterviewRepository
from app.services.ai_service import AIService
from app.services.evaluation_service import EvaluationService
from app.services.sqs_service import SQSService


class AnswerEvaluationListener:
    def __init__(self):
        self.sqs_service = SQSService()

        self.evaluation_service = EvaluationService(
            answer_repository=AnswerRepository(),
            evaluation_repository=EvaluationRepository(),
            interview_question_repository=InterviewQuestionRepository(),
            interview_repository=InterviewRepository(),
            ai_service=AIService(),
        )

    def start(self) -> None:
        print("Answer evaluation listener started...")

        while True:
            messages = self.sqs_service.receive_answer_evaluation_messages()

            if not messages:
                continue

            for message in messages:
                receipt_handle = message["ReceiptHandle"]

                try:
                    body = json.loads(message["Body"])

                    job_type = body.get("job_type")
                    answer_id = body.get("answer_id")

                    if job_type != "EVALUATE_ANSWER":
                        print(f"Skipping unsupported job_type: {job_type}")
                        self.sqs_service.delete_answer_evaluation_message(
                            receipt_handle
                        )
                        continue

                    if not answer_id:
                        print("Skipping message without answer_id")
                        self.sqs_service.delete_answer_evaluation_message(
                            receipt_handle
                        )
                        continue

                    print(f"Evaluating answer: {answer_id}")

                    self.evaluation_service.evaluate_answer(answer_id)

                    self.sqs_service.delete_answer_evaluation_message(
                        receipt_handle
                    )

                    print(f"Finished evaluating answer: {answer_id}")

                except Exception as error:
                    print(f"Failed to process evaluation message: {error}")
                    # Do not delete the message.
                    # SQS will retry it after visibility timeout.

            time.sleep(1)


if __name__ == "__main__":
    listener = AnswerEvaluationListener()
    listener.start()
