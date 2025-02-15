from typing import List
from data.model.chat_message_data_model import ChatMessage


def get_chats(chat_messages: List[ChatMessage]):
    return [
        {
            "role": chat_message.role,
            "content": chat_message.content,
        }
        for chat_message in chat_messages
    ]