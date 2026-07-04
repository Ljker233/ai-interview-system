from pydantic import BaseModel, Field


class CreateUserRequest(BaseModel):
    email: str = Field(min_length=1)
    name: str = Field(min_length=1)
