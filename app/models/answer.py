from pydantic import BaseModel, Field


class SubmitAnswerRequest(BaseModel):
    answer: str = Field(min_length=1)
