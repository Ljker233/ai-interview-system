import logging

from fastapi import APIRouter, HTTPException

from app.models.interview import CreateInterviewRequest
from app.models.answer import SubmitAnswerRequest
from app.repositories.interview_repository import InterviewRepository
from app.repositories.answer_repository import AnswerRepository
from app.services.interview_service import InterviewService
from app.services.question_service import QuestionService
from app.services.sqs_service import SQSService
from app.services.ai_service import AIService
from app.services.answer_service import AnswerService
from app.repositories.interview_question_repository import InterviewQuestionRepository
from app.repositories.question_generation_transaction_repository import QuestionGenerationTransactionRepository
from app.repositories.answer_transaction_repository import AnswerTransactionRepository

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/interviews",
    tags=["interviews"],
)

interview_repository = InterviewRepository()
interview_question_repository = InterviewQuestionRepository()
sqs_service = SQSService()
ai_service = AIService()
transaction_repository = QuestionGenerationTransactionRepository()
answer_repository = AnswerRepository()
answer_transaction_repository = AnswerTransactionRepository()


service = InterviewService(
    interview_repository=interview_repository,
    sqs_service=sqs_service,
)

question_service = QuestionService(
    interview_repository=interview_repository,
    interview_question_repository=interview_question_repository,
    sqs_service=sqs_service,
    ai_service=ai_service,
    transaction_repository=transaction_repository,
)

answer_service = AnswerService(
    answer_repository=answer_repository,
    answer_transaction_repository=answer_transaction_repository,
    interview_repository=interview_repository,
    interview_question_repository=interview_question_repository,
)




@router.post("")
def create_interview(request: CreateInterviewRequest):
    try:
        return service.create_interview(request)
    except ValueError as error:
        logger.exception("Validation error while creating interview")
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as error:
        logger.exception("Unexpected error while creating interview")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create interview: {str(error)}",
        )


@router.get("/{interview_id}")
def get_interview(interview_id: str):
    try:
        return service.get_interview(interview_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Interview not found")
    except Exception as error:
        logger.exception("Unexpected error while getting interview")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get interview: {str(error)}",
        )

@router.get("/{interview_id}/questions")
def get_interview_questions(interview_id: str):
    try:
        return question_service.get_questions_for_interview(interview_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Interview not found")
    except Exception as error:
        logger.exception("Unexpected error while getting interview questions")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get interview questions: {str(error)}",
        )

@router.post("/{interview_id}/questions/{question_id}/answer")
def submit_answer(
    interview_id: str,
    question_id: str,
    request: SubmitAnswerRequest,
):
    try:
        return answer_service.submit_answer(
            interview_id=interview_id,
            question_id=question_id,
            answer_text=request.answer,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit answer: {str(error)}",
        )