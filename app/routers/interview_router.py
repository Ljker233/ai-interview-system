import logging

from fastapi import APIRouter, HTTPException

from app.models.interview import CreateInterviewRequest
from app.repositories.interview_repository import InterviewRepository
from app.services.interview_service import InterviewService
from app.services.sqs_service import SQSService


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/interviews",
    tags=["interviews"],
)

interview_repository = InterviewRepository()
sqs_service = SQSService()

service = InterviewService(
    interview_repository=interview_repository,
    sqs_service=sqs_service,
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
