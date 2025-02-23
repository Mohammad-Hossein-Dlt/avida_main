import uuid
from datetime import datetime
import pytz
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    role: str
    content: str
    timestamp: datetime = Field(default=datetime.now(pytz.UTC))
