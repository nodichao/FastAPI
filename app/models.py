from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

import datetime
import uuid

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    hashed_password: Mapped[str] = mapped_column(nullable=False)


class MessageModel(Base):
    __tablename__ = "messages"


    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    content: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(nullable=False)
    timestamp: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)

    



class ConversationModel(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"),nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)

