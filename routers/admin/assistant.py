from data.model.assistant_data_model import EditAssistant
from utils.db_dependency import db_dependency
from fastapi import APIRouter, status, UploadFile, File, Depends
from actions.assistant_actions import (
    fetch_all_assistant,
    fetch_single_assistant,
    fetch_single_assistant_for_edit,
    insert_assistant,
    edit_assistant
)

router = APIRouter(prefix="/admin/assistant", tags=["Admin-Assistant"])


@router.get("/fetch_assistants/", status_code=status.HTTP_200_OK)
async def insert_agent(
        db: db_dependency,
):
    return await fetch_all_assistant(db=db)


@router.get("/fetch_single_assistant/", status_code=status.HTTP_200_OK)
async def insert_agent(
        db: db_dependency,
        assistant_id: int
):
    return await fetch_single_assistant(db=db, assistant_id=assistant_id)


@router.get("/fetch_single_assistant/for_edit/", status_code=status.HTTP_200_OK)
async def insert_agent(
        db: db_dependency,
        assistant_id: int
):
    return await fetch_single_assistant_for_edit(db=db, assistant_id=assistant_id)


@router.post("/edit_assistant/", status_code=status.HTTP_200_OK)
async def edit_agent(
        db: db_dependency,
        data: EditAssistant = Depends(EditAssistant),
        image_file: UploadFile = File(None),
        delete_image: bool | None = None,
):
    if not data.Id:
        return await insert_assistant(db=db, image_file=image_file, data=data)
    else:
        return await edit_assistant(db, image_file=image_file, data=data, delete_image=delete_image)

