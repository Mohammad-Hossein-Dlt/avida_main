from gpt.gpt_client import gpt_client


def conversation(messages: list):

    completion = gpt_client.chat.completions.create(
        model='gpt-4o',
        messages=messages,
        stream=True
    )

    for chunk in completion:
        response = chunk.choices[0].delta.content
        if response is not None:
            yield response
