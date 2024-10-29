import openai
from ..core.base import BaseChatModel, StructuredOutputMixin, RequestMixin
from ..core.config import ModelConfig
from ..utils.async_stream_processor import async_process_and_convert_stream


class AsyncChatModel(BaseChatModel, RequestMixin):
    def __init__(self, client: openai.AsyncOpenAI, config: ModelConfig):
        super().__init__(client, config)

    async def chat(self, comment: str, return_all: bool = False):
        messages = self.message_handler.create_messages(
            self.config.system_prompt, comment
        )
        chat_request = self.create_request(messages)
        completion = await self.client.chat.completions.create(
            **chat_request.model_dump()
        )

        if not return_all:
            return completion.choices[0].message.content
        else:
            return completion

    async def stream(
        self, comment: str, verbose: bool = True, return_all: bool = False
    ):
        messages = self.message_handler.create_messages(
            self.config.system_prompt, comment
        )
        chat_request = self.create_request(messages, stream=True)
        stream = await self.client.chat.completions.create(**chat_request.model_dump())
        completion = await async_process_and_convert_stream(stream, verbose)

        if not return_all:
            return completion.choices[0].message.content
        else:
            return completion


class AsyncStructuredChatModel(AsyncChatModel, StructuredOutputMixin):
    def __init__(self, client: openai.AsyncOpenAI, config: ModelConfig):
        super().__init__(client, config)
        self.validate_model()
        self.validate_config()

    async def chat(self, content: str, return_all: bool = False):
        messages = self.message_handler.create_messages(
            self.config.system_prompt, content
        )
        chat_request = self.create_structured_request(messages)
        completion = await self.client.chat.completions.create(
            **chat_request.model_dump()
        )
        return self.process_structured_response(completion, return_all)

    async def stream(
        self,
        content: str,
        verbose: bool = True,
        return_all: bool = False,
    ):
        messages = self.message_handler.create_messages(
            self.config.system_prompt, content
        )
        chat_request = self.create_structured_request(messages, stream=True)
        stream = await self.client.chat.completions.create(**chat_request.model_dump())
        completion = await async_process_and_convert_stream(stream, verbose)
        return self.process_structured_response(completion, return_all)
