from typing import List, Dict, Any
import json
from copy import deepcopy

import openai

from ..core.base import BaseChatModel
from ..core.config import ModelConfig
from ..core.constants import STRUCTURED_OUTPUT_MODELS
from ..models import (
    ChatCompletionRequest,
    Message,
    StructuredChatCompletionRequest,
    StructuredResponseFormat,
)
from ..utils.message_handler import MessageHandler
from ..utils.stream_processor import process_and_convert_stream


class SimpleChatModel(BaseChatModel):
    def __init__(self, client: openai.OpenAI, config: ModelConfig):
        super().__init__(client, config)

    def chat(self, comment: str, return_all: bool = False):
        messages = [Message(role="user", content=comment)]
        if self.config.system_prompt:
            messages.insert(
                0, Message(role="system", content=self.config.system_prompt)
            )

        chat_request = ChatCompletionRequest(
            model=self.config.model, messages=messages, **self.config.params
        )

        completion = self.client.client.chat.completions.create(
            **chat_request.model_dump()
        )
        if not return_all:
            return completion.choices[0].message.content
        else:
            return completion

    def stream(self, comment: str, verbose: bool = True, return_all: bool = False):
        messages = self.message_handler.create_messages(
            self.config.system_prompt, comment
        )
        stream_params = deepcopy(self.config.params)
        stream_params.update({"stream_options": {"include_usage": True}})
        stream = self.client.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            stream=True,
            **stream_params,
        )
        completion = process_and_convert_stream(stream, verbose)

        if not return_all:
            return completion.choices[0].message.content
        else:
            return completion


class HistoryChatModel(BaseChatModel):
    def __init__(self, client: openai.OpenAI, config: ModelConfig):
        super().__init__(client, config)
        self.history: List[Message] = []
        self.message_handler = MessageHandler()

    def chat(self, comment: str, return_all: bool = False):
        messages = self.history + self.message_handler.create_messages(
            self.config.system_prompt, Message(role="user", content=comment)
        )
        completion = self.client.client.chat.completions.create(
            model=self.config.model, messages=messages, **self.config.params
        )

        self.add_to_history(comment, completion.choices[0].message.content)

        if not return_all:
            return completion.choices[0].message.content
        else:
            return completion

    def stream(self, comment: str, verbose: bool = True, return_all: bool = False):
        messages = self.history + self.message_handler.create_messages(
            self.config.system_prompt, Message(role="user", content=comment)
        )
        stream_params = deepcopy(self.config.params)
        stream_params.update({"stream_options": {"include_usage": True}})
        stream = self.client.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            stream=True,
            **stream_params,
        )
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


class StructuredChatModel(BaseChatModel):
    def __init__(self, client: openai.OpenAI, config: ModelConfig):
        super().__init__(client, config)
        if self.config.model not in STRUCTURED_OUTPUT_MODELS:
            raise ValueError(
                f"Model {self.config.model} does not support structured output"
            )

    def chat(
        self, content: str, response_format: Dict[str, Any], return_all: bool = False
    ):
        messages = [Message(role="user", content=content)]
        if self.config.system_prompt:
            messages.insert(
                0, Message(role="system", content=self.config.system_prompt)
            )

        chat_request = StructuredChatCompletionRequest(
            model=self.config.model,
            messages=messages,
            response_format=StructuredResponseFormat(**response_format),
            **self.config.params,
        )

        completion = self.client.client.chat.completions.create(
            **chat_request.model_dump()
        )
        if not return_all:
            return json.loads(completion.choices[0].message.content)
        else:
            return completion

    def stream(
        self,
        content: str,
        response_format: Dict[str, Any],
        verbose: bool = True,
        return_all: bool = False,
    ):
        messages = [Message(role="user", content=content)]
        if self.config.system_prompt:
            messages.insert(
                0, Message(role="system", content=self.config.system_prompt)
            )

        chat_request = StructuredChatCompletionRequest(
            model=self.config.model,
            messages=messages,
            response_format=StructuredResponseFormat(**response_format),
            **self.config.params,
        )
        chat_request["stream"] = True
        stream = self.client.client.chat.completions.create(**chat_request.model_dump())
        completion = process_and_convert_stream(stream, verbose)

        if not return_all:
            return json.loads(completion.choices[0].message.content)
        else:
            return completion


def create_gpt(
    gpt_type: str,
    api_key: str,
    model: str,
    params: Dict[str, Any] = None,
    system_prompt: str = "",
) -> BaseChatModel:
    """
    노트북 환경에서 쉽게 GPT 객체를 생성하는 함수

    :param gpt_type: GPT 유형 ('simple', 'history', 'structured')
    :param api_key: OpenAI API 키
    :param model: 사용할 모델 이름
    :param params: 모델 파라미터 (기본값: None)
    :param system_prompt: 시스템 프롬프트 (기본값: "")
    :return: 생성된 GPT 객체
    """
    if params is None:
        params = {}

    return GPTFactory.create_gpt(gpt_type, api_key, model, params, system_prompt)


class GPTFactory:
    @staticmethod
    def create_gpt(
        gpt_type: str,
        api_key: str,
        model: str,
        params: Dict[str, Any],
        system_prompt: str = "",
    ) -> BaseChatModel:
        client = openai.OpenAI(api_key)
        config = ModelConfig(model, params, system_prompt)
        if gpt_type == "simple":
            return SimpleChatModel(client, config)
        elif gpt_type == "history":
            return HistoryChatModel(client, config)
        elif gpt_type == "structured":
            return StructuredChatModel(client, config)
        else:
            raise ValueError(
                "Invalid GPT type. Choose 'simple', 'history', or 'structured'."
            )
