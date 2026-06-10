from fastapi import APIRouter, HTTPException

from app.models.interview import CreateInterviewRequest
from app.repositories.interview_repository import InterviewRepository
from app.services.interview_service import InterviewService


router = APIRouter(
    prefix="/interviews",
    tags=["interviews"]
)

repository = InterviewRepository()
service = InterviewService(repository)


@router.post("")
def create_interview(request: CreateInterviewRequest):
    return service.create_interview(request)


@router.get("/users/{user_id}/history")
def get_user_interviews(user_id: str):
    return service.get_interviews_by_user(user_id)


@router.get("/{interview_id}")
def get_interview(interview_id: str):
    try:
        return service.get_interview(interview_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Interview not found")