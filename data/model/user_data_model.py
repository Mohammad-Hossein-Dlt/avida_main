from pydantic import BaseModel


class SignUp(BaseModel):
    Name: str
    Phone: str
    Password: str
    VerifyCode: str
