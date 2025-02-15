from typing import Annotated
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import InvalidTokenError
from pydantic import BaseModel
from starlette import status

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

SECRET_KEY = '8def8f830990608125a82af8c56c0a787b8c794cacf3ee6cfc17ebe9f9597d20'
ALGORITHM = 'HS256'

tokenBearer = HTTPBearer()

op_tokenBearer = HTTPBearer(auto_error=False)


class TokenData(BaseModel):
    user_name: str | None = None
    user_id: int | None = None
    permission: bool = False


def create_access_token(data: TokenData):
    encoded_jwt = jwt.encode(data.dict(), SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(encoded_token: str, empty_data: bool = False) -> TokenData:
    try:
        payload = jwt.decode(encoded_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_name: str = payload.get("username")
        user_id: int = payload.get("id")
        account_type: str = payload.get("type")
        if user_name is None or user_id is None or account_type is None:
            if empty_data:
                return TokenData()
            else:
                raise credentials_exception
        return TokenData(user_name=user_name, user_id=user_id, account_type=account_type, permission=True)
    except InvalidTokenError:
        if empty_data:
            return TokenData()
        else:
            raise credentials_exception


token_dependency = Annotated[TokenData, Depends(decode_access_token)]
