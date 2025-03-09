from pydantic import BaseModel


class SingleAssistant(BaseModel):
    Id: int | None = None
    Name: str | None = None
    Image: str | None = None
    Description: str | None = None
    Prompt: str | None = None
    Active: bool | None = None

    class Enums:
        Id = "Id"
        Name = "Name"
        Image = "Image"
        Description = "Description"
        Prompt = "Prompt"
        Active = "Active"
