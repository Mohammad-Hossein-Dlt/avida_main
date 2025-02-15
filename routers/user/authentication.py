from data.model.token_data_model import Token
from data.model.user_data_model import SignUp
from main_database.models import User, UserTemp
from fastapi.security import OAuth2PasswordRequestForm
from data.model.response_model import ResponseMessage
from fastapi import APIRouter, HTTPException, status, Depends
from typing import Annotated
from sqlalchemy import and_, or_
from utils.access_token import create_access_token, TokenData
from utils.db_dependency import db_dependency
from argon2 import PasswordHasher

router = APIRouter(prefix="/user/authentication", tags=["User-Authentication"])

password_hasher = PasswordHasher()


@router.post("/sign_up", status_code=status.HTTP_201_CREATED)
async def sign_up_action(
        db: db_dependency,
        sign_up: SignUp = Depends(SignUp),
):
    print(sign_up.Password)
    check = db.query(
        User
    ).where(
        User.Phone == sign_up.Phone
    ).first()

    verify_code = db.query(
        UserTemp
    ).where(
        and_(
            UserTemp.Phone == sign_up.Phone,
            UserTemp.VerifyCode == sign_up.VerifyCode
        )
    ).first()

    # verify_code = True

    if check:
        raise HTTPException(201, "user already signed up!")

    if verify_code is None:
        raise HTTPException(403, "you are not verified")

    user = User()
    user.Name = sign_up.Name.strip()
    user.Phone = sign_up.Phone.strip()
    user.Password = password_hasher.hash(sign_up.Password.encode("utf-8"))
    db.add(user)

    db.commit()

    return ResponseMessage(Error=False, Content="User has been signed up!")


@router.post("/sign_in", status_code=status.HTTP_201_CREATED)
async def sign_in(
        db: db_dependency,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = db.query(
        User
    ).where(
        or_(
            User.Phone == form_data.username,
            User.UserName == form_data.username,
        )
    ).first()

    verify_code = db.query(
        UserTemp
    ).where(
        and_(
            UserTemp.Phone == form_data.username,
        )

    ).first()

    if user is None:
        raise HTTPException(403, "You are not signed up")

    password_check = password_hasher.verify(
        hash=user.Password.encode(),
        password=form_data.password.encode("utf-8"),
    )

    verify_code_check = verify_code.VerifyCode == form_data.password if verify_code else False

    if password_check or verify_code_check:
        token = TokenData()
        token.user_name = user.UserName
        token.user_id = user.Id
        access_token = create_access_token(token)
        return Token(access_token=access_token, token_type="bearer")

    if not password_check or not verify_code:
        raise HTTPException(403, "Incorrect password or verify code")
