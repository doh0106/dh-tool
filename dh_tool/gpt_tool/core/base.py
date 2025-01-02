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
from ..utils.stream_processor import process_and_convert_stream


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

    def chat(self, content: str, return_all: bool = False):
        messages = self._prepare_messages(content)
        request = self._create_request(messages)
        completion = self._execute_request(request)
        self._handle_response(content, completion)
        return self._process_response(completion, return_all)

    def stream(self, content: str, verbose: bool = True, return_all: bool = False):
        """Template method for stream completion"""
        messages = self._prepare_messages(content)
        request = self._create_request(
            messages, stream=True, stream_options={"include_usage": True}
        )
        stream = self._execute_request(request)
        completion = process_and_convert_stream(stream, verbose)
        self._handle_response(content, completion)
        return self._process_response(completion, return_all)

    @abstractmethod
    def _prepare_messages(self, content: str) -> List[Message]:
        """Prepare messages for the request"""
        pass

    @abstractmethod
    def _create_request(
        self, messages: List[Message], **kwargs
    ) -> ChatCompletionRequest:
        """Create request object"""
        pass

    def _execute_request(self, request):
        """Execute the chat completion request"""
        return self.client.chat.completions.create(**request.model_dump())

    def _handle_response(self, content: str, completion) -> None:
        """Handle the response (e.g., save to history)"""
        pass

    def _process_response(self, completion, return_all: bool):
        """Process the completion response"""
        if not return_all:
            return completion.choices[0].message.content
        return completion

    def embed(self, texts, return_all: bool = False):
        if isinstance(texts, str):
            texts = [texts]
        response = self.client.embeddings.create(input=texts, model=self.model_emb)
        if not return_all:
            return [r.embedding for r in response.data]
        else:
            return response

    @staticmethod
    def calculate_price(
        first_param,
        second_param=None,
        model_name: str = None,
        exchange_rate: float = 1400,
    ) -> float:
        """Calculate the price of API usage.

        Args:
            first_param: Either a completion object or prompt_tokens
            second_param: completion_tokens (when first_param is prompt_tokens)
            model_name: Required when using token counts directly
            exchange_rate: Optional exchange rate to local currency
        """
        if hasattr(first_param, "model"):  # Completion object case
            completion = first_param
            model_name = completion.model
            prompt_tokens = completion.usage.prompt_tokens
            completion_tokens = completion.usage.completion_tokens
            cached_tokens = completion.usage.prompt_tokens_details.cached_tokens
        else:  # Token counts case
            prompt_tokens = first_param
            completion_tokens = second_param
            cached_tokens = 0  # 기본 값
            if model_name is None:
                raise ValueError("model_name is required when providing token counts")

        if model_name not in MODEL_PRICE:
            print(f"{model_name} not in price dict")
            return 0

        # 가격 계산
        token_prices = MODEL_PRICE[model_name]
        prompt_price = (prompt_tokens - cached_tokens) * token_prices["prompt_tokens"]
        completion_price = completion_tokens * token_prices["completion_tokens"]

        # 추가 가격 계산 (예: cached_tokens 처리)
        cached_price = cached_tokens * token_prices["prompt_tokens"] * 0.5

        total_price = exchange_rate * (prompt_price + completion_price + cached_price)
        return total_price


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
