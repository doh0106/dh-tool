from abc import ABC, abstractmethod
from typing import List

import openai
import json

from .config import ModelConfig
from .constants import MODEL_PRICE, STRUCTURED_OUTPUT_MODELS
from ..models import (
    Message,
    ChatCompletionRequest,
    StructuredChatCompletionRequest,
)
from ..utils.message_handler import MessageHandler


class RequestMixin:
    def create_request(
        self, messages: List[Message], **kwargs
    ) -> ChatCompletionRequest:
        return ChatCompletionRequest(
            model=self.config.model,
            messages=messages,
            **{**self.config.params, **kwargs},
        )


class BaseChatModel(ABC):
    def __init__(
        self,
        client: openai.OpenAI,
        config: ModelConfig,
    ):
        self.client = client
        self.config = config
        self.model_emb = "text-embedding-3-large"
        self.message_handler = MessageHandler()

    @abstractmethod
    def chat(self, comment: str, return_all: bool = False):
        pass

    @abstractmethod
    def stream(self, comment: str, verbose: bool = True, return_all: bool = False):
        pass

    def embed(self, texts, return_all: bool = False):
        if isinstance(texts, str):
            texts = [texts]
        response = self.client.client.embeddings.create(
            input=texts, model=self.model_emb
        )
        if not return_all:
            return [r.embedding for r in response.data]
        else:
            return response

    @staticmethod
    def calculate_price(
        prompt_tokens: int,
        completion_tokens: int,
        model_name: str,
        exchange_rate: float = 1400,
    ) -> float:
        if model_name in MODEL_PRICE:
            token_prices = MODEL_PRICE[model_name]
            return exchange_rate * (
                prompt_tokens * token_prices[0] + completion_tokens * token_prices[1]
            )
        print(f"{model_name} not in price dict")
        return 0


class HistoryMixin:
    def __init__(self, max_history_length: int = 10):
        self.history: List[Message] = []
        self.max_history_length = max_history_length

    def clear_history(self):
        self.history = []

    def add_to_history(self, user_message: str, assistant_message: str):
        self.history.append({"role": "user", "content": user_message})
        self.history.append({"role": "assistant", "content": assistant_message})

        # 최대 길이를 초과하면 가장 오래된 메시지 쌍을 제거
        while len(self.history) > self.max_history_length * 2:
            self.history.pop(0)
            self.history.pop(0)

    def get_messages_with_system_prompt(self, system_prompt: str) -> List[Message]:
        return [{"role": "system", "content": system_prompt}] + self.history


class StructuredOutputMixin:
    def validate_model(self):
        if self.config.model not in STRUCTURED_OUTPUT_MODELS:
            raise ValueError(
                f"Model {self.config.model} does not support structured output"
            )

    def validate_config(self):
        if not self.config.params["response_format"]:
            raise ValueError(
                "response_format must be provided in config for structured output"
            )

    def create_structured_request(
        self,
        messages: List[Message],
        **kwargs,
    ) -> StructuredChatCompletionRequest:
        return StructuredChatCompletionRequest(
            model=self.config.model,
            messages=messages,
            **{**self.config.params, **kwargs},
        )

    def process_structured_response(self, completion, return_all: bool):
        if not return_all:
            return json.loads(completion.choices[0].message.content)
        else:
            return completion
