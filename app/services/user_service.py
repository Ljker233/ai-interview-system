import re
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import UploadFile

from app.models.user import CreateUserRequest
from app.repositories.user_repository import UserRepository
from app.services.s3_service import S3Service


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        s3_service: S3Service,
    ):
        self.user_repository = user_repository
        self.s3_service = s3_service

    def create_user(self, request: CreateUserRequest) -> dict:
        user_id = str(uuid4())
        now = self._now_iso()

        user = {
            "user_id": user_id,
            "email": request.email,
            "name": request.name,
            "created_at": now,
            "updated_at": now,
        }

        self.user_repository.save(user)

        return user

    def get_user(self, user_id: str) -> dict:
        user = self.user_repository.find_by_id(user_id)

        if user is None:
            raise ValueError("User not found")

        return user

    def upload_resume(
        self,
        user_id: str,
        file: UploadFile,
    ) -> dict:
        user = self.user_repository.find_by_id(user_id)

        if user is None:
            raise ValueError("User not found")

        self._validate_resume_file(file)

        now = self._now_iso()

        s3_key = self._build_resume_s3_key(
            user_id=user_id,
            file_name=file.filename,
        )

        upload_result = self.s3_service.upload_resume_file(
            file=file,
            s3_key=s3_key,
        )

        current_resume = {
            "file_name": file.filename,
            "s3_bucket": upload_result["s3_bucket"],
            "s3_key": upload_result["s3_key"],
            "content_type": file.content_type or "application/octet-stream",
            "uploaded_at": now,
        }

        self.user_repository.update_current_resume(
            user_id=user_id,
            current_resume=current_resume,
            updated_at=now,
        )

        return {
            "user_id": user_id,
            "file_name": file.filename,
            "s3_bucket": upload_result["s3_bucket"],
            "s3_key": upload_result["s3_key"],
            "message": "Resume uploaded successfully",
        }

    def get_resume_download_url(self, user_id: str) -> dict:
        user = self.get_user(user_id)

        current_resume = user.get("current_resume")
        if not current_resume:
            raise ValueError("User has not uploaded a resume")

        download_url = self.s3_service.generate_presigned_download_url(
            s3_key=current_resume["s3_key"],
        )

        return {
            "user_id": user_id,
            "file_name": current_resume["file_name"],
            "download_url": download_url,
            "expires_in_seconds": 3600,
        }

    def _build_resume_s3_key(
        self,
        user_id: str,
        file_name: str,
    ) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        safe_file_name = self._sanitize_file_name(file_name)

        return f"resumes/{user_id}/{timestamp}_{safe_file_name}"

    def _sanitize_file_name(self, file_name: str) -> str:
        file_name = file_name.strip()
        file_name = file_name.replace(" ", "_")

        return re.sub(r"[^a-zA-Z0-9._-]", "", file_name)

    def _validate_resume_file(self, file: UploadFile) -> None:
        if not file.filename:
            raise ValueError("File name is required")

        allowed_content_types = {
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }

        if file.content_type not in allowed_content_types:
            raise ValueError(
                "Only PDF and DOCX resume files are supported"
            )

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()
