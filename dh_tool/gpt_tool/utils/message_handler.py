from typing import List
from ..models import Message


class MessageHandler:
    @staticmethod
    def create_messages(system_prompt: str, user_message: str) -> List[Message]:
        messages = []
        if system_prompt:
            messages.append(Message(role="system", content=system_prompt))
        messages.append(Message(role="user", content=user_message))
        return messages

    @staticmethod
    def create_messages_with_history(
        system_prompt: str, user_message: str, history: List[dict]
    ) -> List[Message]:
        messages = []
        if system_prompt:
            messages.append(Message(role="system", content=system_prompt))
        # 히스토리 추가
        for message in history:
            messages.append(Message(**message))
        # 현재 메시지 추가
        messages.append(Message(role="user", content=user_message))
        return messages
