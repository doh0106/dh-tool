import openai

from ..core.base import BaseChatModel, HistoryMixin, StructuredOutputMixin, RequestMixin
from ..core.config import ModelConfig
from ..utils.stream_processor import process_and_convert_stream


class SimpleChatModel(BaseChatModel, RequestMixin):
    def __init__(self, client: openai.OpenAI, config: ModelConfig):
        super().__init__(client, config)

    def chat(self, comment: str, return_all: bool = False):
        messages = self.message_handler.create_messages(
            self.config.system_prompt, comment
        )
        chat_request = self.create_request(messages)
        for m in messages:
            print(m)
        completion = self.client.chat.completions.create(**chat_request.model_dump())

        if not return_all:
            return completion.choices[0].message.content
        else:
            return completion

    def stream(self, comment: str, verbose: bool = True, return_all: bool = False):
        messages = self.message_handler.create_messages(
            self.config.system_prompt, comment
        )
        chat_request = self.create_request(messages, stream=True)
        stream = self.client.chat.completions.create(**chat_request.model_dump())
        completion = process_and_convert_stream(stream, verbose)

        if not return_all:
            return completion.choices[0].message.content
        else:
            return completion


class HistoryChatModel(BaseChatModel, HistoryMixin, RequestMixin):
    def __init__(
        self, client: openai.OpenAI, config: ModelConfig, max_history_length: int = 10
    ):
        BaseChatModel.__init__(self, client, config)
        HistoryMixin.__init__(self, max_history_length)

    def chat(self, comment: str, return_all: bool = False):
        messages = self.get_messages_with_system_prompt(self.config.system_prompt)
        messages.append({"role": "user", "content": comment})

        chat_request = self.create_request(messages)
        # print(messages)
        for m in messages:
            print(m)
        completion = self.client.chat.completions.create(**chat_request.model_dump())

        self.add_to_history(comment, completion.choices[0].message.content)

        if not return_all:
            return completion.choices[0].message.content
        else:
            return completion

    def stream(self, comment: str, verbose: bool = True, return_all: bool = False):
        messages = self.get_messages_with_system_prompt(self.config.system_prompt)
        messages.append({"role": "user", "content": comment})

        chat_request = self.create_request(messages, stream=True)
        stream = self.client.chat.completions.create(**chat_request.model_dump())
        completion = process_and_convert_stream(stream, verbose)

        self.add_to_history(comment, completion.choices[0].message.content)

        if not return_all:
            return completion.choices[0].message.content
        else:
            return completion

    def clear_history(self):
        self.history = []

    def add_to_history(self, user_message: str, assistant_message: str):
        self.history.append({"role": "user", "content": user_message})
        self.history.append({"role": "assistant", "content": assistant_message})


class StructuredChatModel(BaseChatModel, StructuredOutputMixin, RequestMixin):
    def __init__(self, client: openai.OpenAI, config: ModelConfig):
        super().__init__(client, config)
        self.validate_model()
        self.validate_config()

    def chat(self, content: str, return_all: bool = False):
        messages = self.message_handler.create_messages(
            self.config.system_prompt, content
        )
        chat_request = self.create_structured_request(messages)
        completion = self.client.chat.completions.create(**chat_request.model_dump())
        return self.process_structured_response(completion, return_all)

    def stream(
        self,
        content: str,
        verbose: bool = True,
        return_all: bool = False,
    ):
        messages = self.message_handler.create_messages(
            self.config.system_prompt, content
        )
        chat_request = self.create_structured_request(messages, stream=True)
        stream = self.client.chat.completions.create(**chat_request.model_dump())
        completion = process_and_convert_stream(stream, verbose)
        return self.process_structured_response(completion, return_all)


class HistoryStructuredChatModel(
    BaseChatModel, HistoryMixin, StructuredOutputMixin, RequestMixin
):
    def __init__(
        self, client: openai.OpenAI, config: ModelConfig, max_history_length: int = 10
    ):
        BaseChatModel.__init__(self, client, config)
        HistoryMixin.__init__(self, max_history_length)
        self.validate_model()
        self.validate_config()

    def chat(
        self,
        content: str,
        return_all: bool = False,
    ):
        messages = self.get_messages_with_system_prompt(self.config.system_prompt)
        messages.append({"role": "user", "content": content})

        chat_request = self.create_structured_request(messages)
        completion = self.client.chat.completions.create(**chat_request.model_dump())
        response = self.process_structured_response(completion, return_all)

        self.add_to_history(content, completion.choices[0].message.content)
        return response

    def stream(
        self,
        content: str,
        verbose: bool = True,
        return_all: bool = False,
    ):
        messages = self.get_messages_with_system_prompt(self.config.system_prompt)
        messages.append({"role": "user", "content": content})

        chat_request = self.create_structured_request(messages, stream=True)
        stream = self.client.chat.completions.create(**chat_request.model_dump())
        completion = process_and_convert_stream(stream, verbose)
        response = self.process_structured_response(completion, return_all)

        self.add_to_history(content, completion.choices[0].message.content)
        return response
