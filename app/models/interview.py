from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class InterviewType(str, Enum):
    coding = "coding"
    behavioral = "behavioral"
    system_design = "system_design"


class InterviewQuestionResponse(BaseModel):
    question_id: str
    interview_id: str
    type: InterviewType
    question: str
    question_order: int
    status: str
    created_at: str


class CreateInterviewRequest(BaseModel):
    user_id: str
    interview_types: List[InterviewType] = Field(min_length=1)
    target_role: str
    difficulty: str


class CreateInterviewResponse(BaseModel):
    interview_id: str
    user_id: str
    interview_types: List[InterviewType]
    target_role: str
    difficulty: str
    status: str
    created_at: str
    questions: List[InterviewQuestionResponse]
