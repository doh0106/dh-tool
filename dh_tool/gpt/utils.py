from typing import List, Dict


class MessageHandler:
    @staticmethod
    def create_messages(system_prompt: str, user_message: str) -> List[Dict[str, str]]:
        messages = [{"role": "user", "content": user_message}]
        if system_prompt:
            messages.insert(0, {"role": "system", "content": system_prompt})
        return messages
