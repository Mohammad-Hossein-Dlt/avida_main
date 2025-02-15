from pydantic import BaseModel


class EditAssistant(BaseModel):
    Id: int | None = None
    Name: str | None = None
    Description: str | None = None
    Prompt: str | None = None
    Active: bool | None = None


class SingleAssistant(BaseModel):
    Id: int | None = None
    Name: str | None = None
    Image: str | None = None
    Description: str | None = None
    Prompt: str | None = None
    Active: bool | None = None
