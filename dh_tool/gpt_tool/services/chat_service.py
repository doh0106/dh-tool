import openai
from typing import List

from ..core.base import BaseChatModel, HistoryMixin, StructuredOutputMixin, RequestMixin
from ..core.config import ModelConfig
from ..models import Message, ChatCompletionRequest


class SimpleChatModel(BaseChatModel, RequestMixin):
    def __init__(self, client: openai.OpenAI, config: ModelConfig):
        super().__init__(client, config)

    def _prepare_messages(self, content: str) -> List[Message]:
        return self.message_handler.create_messages(self.config.system_prompt, content)

    def _create_request(
        self, messages: List[Message], **kwargs
    ) -> ChatCompletionRequest:
        return self.create_request(messages, **kwargs)


class HistoryChatModel(BaseChatModel, HistoryMixin, RequestMixin):
    def __init__(
        self, client: openai.OpenAI, config: ModelConfig, max_history_length: int = 10
    ):
        BaseChatModel.__init__(self, client, config)
        HistoryMixin.__init__(self, max_history_length)

    def _prepare_messages(self, content: str) -> List[Message]:
        messages = self.message_handler.create_messages(
            self.config.system_prompt, content
        )
        if self.config.system_prompt:
            messages.insert(1, self.history)
        else:
            messages.insert(0, self.history)
        return messages

    def _create_request(
        self, messages: List[Message], **kwargs
    ) -> ChatCompletionRequest:
        return self.create_request(messages, **kwargs)

    def _handle_response(self, content: str, completion) -> None:
        self.add_to_history(content, completion.choices[0].message.content)


class StructuredChatModel(BaseChatModel, StructuredOutputMixin, RequestMixin):
    def __init__(self, client: openai.OpenAI, config: ModelConfig):
        super().__init__(client, config)
        self.validate_model()
        self.validate_config()

    def _prepare_messages(self, content: str) -> List[Message]:
        return self.message_handler.create_messages(self.config.system_prompt, content)

    def _create_request(
        self, messages: List[Message], **kwargs
    ) -> ChatCompletionRequest:
        return self.create_structured_request(messages, **kwargs)

    def _process_response(self, completion, return_all: bool):
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

    def _prepare_messages(self, content: str) -> List[Message]:
        messages = self.message_handler.create_messages(
            self.config.system_prompt, content
        )
        if self.config.system_prompt:
            messages.insert(1, self.history)
        else:
            messages.insert(0, self.history)
        return messages

    def _create_request(
        self, messages: List[Message], **kwargs
    ) -> ChatCompletionRequest:
        return self.create_structured_request(messages, **kwargs)

    def _handle_response(self, content: str, completion) -> None:
        self.add_to_history(content, completion.choices[0].message.content)

    def _process_response(self, completion, return_all: bool):
        return self.process_structured_response(completion, return_all)
