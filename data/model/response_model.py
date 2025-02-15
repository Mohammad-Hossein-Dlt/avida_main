from typing import Any
from pydantic import BaseModel


class ResponseMessage(BaseModel):
    Error: bool = True
    Content: Any = "an error occurred!"
