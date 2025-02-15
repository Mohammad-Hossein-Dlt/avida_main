from datetime import datetime
import pytz
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str  # "user"، "assistant" یا "system"
    content: str
    timestamp: datetime = Field(default=datetime.now(pytz.UTC))

