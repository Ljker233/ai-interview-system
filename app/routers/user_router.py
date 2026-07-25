from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.user import CreateUserRequest
from app.repositories.user_repository import UserRepository
from app.services.s3_service import S3Service
from app.services.user_service import UserService


router = APIRouter()

user_service = UserService(
    user_repository=UserRepository(),
    s3_service=S3Service(),
)


@router.post("")
def create_user(request: CreateUserRequest):
    try:
        return user_service.create_user(request)
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create user: {str(error)}",
        )


@router.get("/{user_id}")
def get_user(user_id: str):
    try:
        return user_service.get_user(user_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user: {str(error)}",
        )


@router.post("/{user_id}/resume")
def upload_resume(
    user_id: str,
    file: UploadFile = File(...),
):
    try:
        return user_service.upload_resume(
            user_id=user_id,
            file=file,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload resume: {str(error)}",
        )


@router.get("/{user_id}/resume/download-url")
def get_resume_download_url(user_id: str):
    try:
        return user_service.get_resume_download_url(user_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate download URL: {str(error)}",
        )
