from fastapi import APIRouter, HTTPException

from app.models.interview import CreateInterviewRequest
from app.repositories.interview_question_repository import InterviewQuestionRepository
from app.repositories.interview_repository import InterviewRepository
from app.services.interview_service import InterviewService


router = APIRouter(
    prefix="/interviews",
    tags=["interviews"],
)

interview_repository = InterviewRepository()
question_repository = InterviewQuestionRepository()

service = InterviewService(
    interview_repository=interview_repository,
    question_repository=question_repository,
)


@router.post("")
def create_interview(request: CreateInterviewRequest):
    try:
        return service.create_interview(request)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    # except Exception:
    #     raise HTTPException(status_code=500, detail="Failed to create interview")


@router.get("/users/{user_id}/history")
def get_user_interviews(user_id: str):
    try:
        return service.get_interviews_by_user(user_id)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to get user interview history")


@router.get("/{interview_id}")
def get_interview(interview_id: str):
    try:
        return service.get_interview(interview_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Interview not found")
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to get interview")
