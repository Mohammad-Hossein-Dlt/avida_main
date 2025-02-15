from gpt.gpt_client import gpt_client


def conversation(messages: list):

    completion = gpt_client.chat.completions.create(
        model='gpt-4o',
        messages=messages,
    )

    response = completion.choices[0].message.content

    return response
