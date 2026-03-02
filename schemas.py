from pydantic import BaseModel, ConfigDict, Field, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=120)


class FeedbackBase(BaseModel):
    rating: int = Field(ge=0, le=10)
    feedback: str = Field(min_length=3)


class FeedbackCreate(FeedbackBase):
    user_id: int


class FeedbackUpdate(BaseModel):
    rating: int | None = Field(default=None, ge=0, le=10)
    feedback: str | None = Field(default=None, min_length=3)


class FeedbackResponse(FeedbackBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    date_posted: datetime
    author: UserResponse
