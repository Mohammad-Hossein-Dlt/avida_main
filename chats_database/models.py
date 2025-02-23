from datetime import datetime
from typing import List
import pytz
from beanie import Document
from pydantic import Field
from data.model.chat_message_data_model import ChatMessage


class ChatSession(Document):
    user_id: str
    title: str
    messages: List[ChatMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(pytz.UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(pytz.UTC))

    class Settings:
        name = "chat_sessions"
