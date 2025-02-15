from main_database.models import Assistant
from data.model.assistant_data_model import SingleAssistant


def get_assistant_for_edit(
        assistant: Assistant | None = None
) -> SingleAssistant:

    data = SingleAssistant()

    if assistant:

        data.Id = assistant.Id
        data.Name = assistant.Name
        data.Image = assistant.Image
        data.Description = assistant.Description
        data.Prompt = assistant.Prompt
        data.Active = assistant.Active

    return data


def get_single_assistant(
        assistant: Assistant | None = None
) -> SingleAssistant:

    data = SingleAssistant()

    if assistant:

        data.Id = assistant.Id
        data.Name = assistant.Name
        data.Image = assistant.Image
        data.Description = assistant.Description
        data.Active = assistant.Active

    del data.Prompt

    return data
