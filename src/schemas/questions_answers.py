from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, ConfigDict


class AnswerCreate(BaseModel):
    user_id: str = Field(..., min_length=1, description="Идентификатор пользователя")
    text: str = Field(..., min_length=1, description="Текст ответа")


class AnswerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question_id: int
    user_id: str
    text: str
    created_at: datetime


class QuestionCreate(BaseModel):
    text: str = Field(..., min_length=1, description="Текст вопроса")


class QuestionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    created_at: datetime
    answers: List[AnswerRead] = Field(default_factory=list)
