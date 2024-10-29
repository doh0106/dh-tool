import openai
from typing import List

from ..core.base import BaseChatModel, StructuredOutputMixin, RequestMixin
from ..core.config import ModelConfig
from ..models import Message, ChatCompletionRequest
from ..utils.async_stream_processor import async_process_and_convert_stream


class AsyncChatModel(BaseChatModel, RequestMixin):
    def __init__(self, client: openai.AsyncOpenAI, config: ModelConfig):
        super().__init__(client, config)

    def _prepare_messages(self, content: str) -> List[Message]:
        return self.message_handler.create_messages(self.config.system_prompt, content)

    def _create_request(
        self, messages: List[Message], **kwargs
    ) -> ChatCompletionRequest:
        return self.create_request(messages, **kwargs)

    async def _execute_request(self, request):
        return await self.client.chat.completions.create(**request.model_dump())

    async def chat(self, content: str, return_all: bool = False):
        messages = self._prepare_messages(content)
        request = self._create_request(messages)
        completion = await self._execute_request(request)
        self._handle_response(content, completion)
        return self._process_response(completion, return_all)

    async def stream(
        self, content: str, verbose: bool = True, return_all: bool = False
    ):
        messages = self._prepare_messages(content)
        request = self._create_request(
            messages, stream=True, stream_options={"include_usage": True}
        )
        stream = await self._execute_request(request)
        completion = await async_process_and_convert_stream(stream, verbose)
        self._handle_response(content, completion)
        return self._process_response(completion, return_all)


class AsyncStructuredChatModel(AsyncChatModel, StructuredOutputMixin):
    def __init__(self, client: openai.AsyncOpenAI, config: ModelConfig):
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
