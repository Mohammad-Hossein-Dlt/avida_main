from fastapi import APIRouter, status
from random import randint
from data.model.response_model import ResponseMessage
from main_database.models import UserTemp
from utils.db_dependency import db_dependency
from datetime import datetime, timedelta
import pytz


router = APIRouter(tags=["General-Verify-Phone"])


@router.post("/verify_phone", status_code=status.HTTP_201_CREATED)
async def verify_user(
        db: db_dependency,
        phone: str,
):
    phone = phone.strip()
    temp = db.query(UserTemp).where(UserTemp.Phone == phone).all()

    for t in temp:
        db.delete(t)

    db.commit()

    verify_code = randint(1000, 10000)

    # rest_client = rest.Rest_Client('Hosein0098', '00316dce-bdbe-4f0f-821a-8673c0fb3f2d')
    # result = rest_client.SendSMS(phone, '50004000890867', f'کد تایید شما: {verify_code}', False)
    #
    # if not result:
    #     raise HTTPException(404, "an error occurred!")

    temp = UserTemp()
    temp.Phone = phone
    temp.VerifyCode = verify_code
    temp.ExpirationDate = datetime.now(pytz.UTC) + timedelta(minutes=5)
    db.add(temp)
    db.commit()

    return ResponseMessage(
        Error=False,
        Content={
            'Message': 'verify code has been set!',
            "Code": verify_code,
        },
    )
