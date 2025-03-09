import pathlib
import uuid
from data.model.response_model import ResponseMessage
from storage.storage import Buckets, create_directory, upload_file, storage_delete_file
from utils.db_dependency import db_dependency
from fastapi import UploadFile, File
from data.model.assistant_data_model import SingleAssistant
from utils.check_nulls import none_analysis
from utils.path_manager import make_path
from fastapi import HTTPException
from main_database.models import Assistant
from common.assistant_common import get_assistant_for_edit, get_single_assistant


async def fetch_all_assistant(
        db: db_dependency,
):
    assistant = db.query(
        Assistant
    ).all()

    return [
        get_single_assistant(i) for i in assistant
    ]


async def fetch_single_assistant(
        db: db_dependency,
        assistant_id: int
):
    assistant = db.query(
        Assistant
    ).where(
        Assistant.Id == assistant_id
    ).first()

    return get_single_assistant(assistant)


async def fetch_single_assistant_for_edit(
        db: db_dependency,
        assistant_id: int
):
    assistant = db.query(
        Assistant
    ).where(
        Assistant.Id == assistant_id
    ).first()

    return get_assistant_for_edit(assistant)


async def insert_assistant(
        db: db_dependency,
        data: SingleAssistant,
        image_file: UploadFile = File(None),
):
    analysis = none_analysis(data, [data.Enums.Id, data.Enums.Image])

    if analysis.have_none:
        raise HTTPException(422,
                            f"{'(' if len(analysis.nones) > 1 else ''}{', '.join(analysis.nones)}{')' if len(analysis.nones) > 1 else ''} submitted incorrectly!")

    assistant = Assistant()
    assistant.Name = data.Name
    assistant.Prompt = data.Prompt
    assistant.Description = data.Description
    assistant.Active = data.Active

    db.add(assistant)
    db.commit()

    root_path = make_path(assistant.DirectoryName, is_file=False)
    directory = create_directory(bucket_name=Buckets.AVIDA_STORAGE, path=root_path)

    if image_file and directory:

        file_name = uuid.uuid4().hex + pathlib.Path(image_file.filename).suffix
        file_path = make_path(root_path, file_name, is_file=True)

        uploaded = upload_file(
            file=image_file.file,
            bucket_name=Buckets.AVIDA_STORAGE,
            path=file_path,
        )

        if uploaded:
            assistant.Image = file_name
            db.commit()

    return ResponseMessage(
        Error=False,
        Content={
            'Message': 'assistant created',
            'Assistant_Id': assistant.Id,
        },
    )


async def edit_assistant(
        db: db_dependency,
        data: SingleAssistant,
        image_file: UploadFile = File(None),
        delete_image: bool | None = None,
):
    assistant = db.query(
        Assistant
    ).where(
        Assistant.Id == data.Id
    ).first()

    assistant.Name = data.Name if data.Name is not None else assistant.Name
    assistant.Prompt = data.Prompt if data.Prompt is not None else assistant.Prompt
    assistant.Description = data.Description if data.Description is not None else assistant.Description
    assistant.Active = data.Active if data.Active is not None else assistant.Active

    main_path = make_path(assistant.DirectoryName, is_file=False)

    def delete_image_action(image: str):
        try:
            delete_previous = make_path(main_path, image, is_file=True)
            storage_delete_file(delete_previous, Buckets.AVIDA_STORAGE)
        except Exception as ex_2:
            print(ex_2)

    if image_file and not delete_image:
        previous_image_file_name = assistant.Image
        new_image_file_name = uuid.uuid4().hex + pathlib.Path(image_file.filename).suffix
        try:

            # Upload the file

            new_image_path = make_path(main_path, new_image_file_name, is_file=True)
            uploaded = upload_file(
                file=image_file.file,
                bucket_name=Buckets.AVIDA_STORAGE,
                path=new_image_path,
            )
        except Exception as ex:

            # Run if an error occurred while uploading the file, delete the newly uploaded file

            print(ex)
            delete_image_action(new_image_file_name)
        else:

            # Run if uploading the file where OK,
            # delete the previous uploaded file and set the name of the new file to main_database

            if previous_image_file_name:
                try:

                    # Run if previous file exist

                    delete_image_action(previous_image_file_name)
                except Exception as ex_1:

                    # Run if an error occurred while deleting the previous file, delete the newly uploaded file

                    print(ex_1)
                    delete_image_action(new_image_file_name)
                else:

                    # Set the name of the new file to main_database

                    assistant.Image = new_image_file_name

            else:

                # Set the name of the new file to main_database

                assistant.Image = new_image_file_name

    elif not image_file and delete_image:
        try:
            delete_image_action(assistant.Image)
        except Exception as ex_1:
            print(ex_1)
        else:
            assistant.Image = None

    db.commit()

    return ResponseMessage(
        Error=False,
        Content={
            'Message': 'assistant edited',
            'Assistant_Id': assistant.Id,
        },
    )
