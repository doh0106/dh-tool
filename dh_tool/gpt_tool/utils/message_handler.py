from typing import List, Dict
from ..models import Message


class MessageHandler:
    @staticmethod
    def create_messages(system_prompt: str, user_message: str) -> List[Message]:
        messages = [Message(role="user", content=user_message)]
        if system_prompt:
            messages.insert(0, Message(role="system", content=system_prompt))
        return messages
