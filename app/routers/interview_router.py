import logging

from fastapi import APIRouter, HTTPException

from app.models.interview import CreateInterviewRequest
from app.repositories.interview_repository import InterviewRepository
from app.services.interview_service import InterviewService
from app.services.question_service import QuestionService
from app.services.sqs_service import SQSService
from app.services.ai_service import AIService
from app.repositories.interview_question_repository import InterviewQuestionRepository
from app.repositories.question_generation_transaction_repository import QuestionGenerationTransactionRepository

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
