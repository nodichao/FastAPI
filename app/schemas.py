from pydantic import BaseModel, EmailStr, Field
import datetime


class User(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str = Field(min_length=5, max_length=100)
    password: str = Field(min_length=8, max_length=100)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    id: str = Field(default_factory=str)

class Conversation(BaseModel):
    user_id: str = Field(min_length=1, max_length=50)
    messages: list[Message] = Field(default_factory=list)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)

class Message(BaseModel):
    conversation_id: str | None = Field(default=None, min_length=1, max_length=50)
    content: str = Field(min_length=1, max_length=1000)
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str