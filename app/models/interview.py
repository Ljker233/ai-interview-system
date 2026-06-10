from enum import Enum
from typing import List
from pydantic import BaseModel, Field
class InterviewType(str, Enum):
    coding = "coding"
    behavioral = "behavioral"
    system_design = "system_design"
class InterviewQuestion(BaseModel):
    type: InterviewType
    question: str
class CreateInterviewRequest(BaseModel):
    user_id: str
    interview_types: List[InterviewType] = Field(min_length=1)
    target_role: str
    difficulty: str
class InterviewResponse(BaseModel):
    interview_id: str
    user_id: str
    interview_types: List[InterviewType]
    target_role: str
    difficulty: str
    questions: List[InterviewQuestion]
    status: str