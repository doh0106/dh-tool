from ..core.base import RequestFactory
from ..models import (
    ChatCompletionRequest,
    Message,
    StructuredChatCompletionRequest,
    StructuredResponseFormat,
)
from typing import List, Dict, Any


class SimpleRequestFactory(RequestFactory):
    def create_request(
        self, model: str, messages: List[Message], params: Dict[str, Any]
    ) -> ChatCompletionRequest:
        return ChatCompletionRequest(model=model, messages=messages, **params)


class StructuredRequestFactory(RequestFactory):
    def create_request(
        self,
        model: str,
        messages: List[Message],
        params: Dict[str, Any],
        response_format: Dict[StructuredResponseFormat],
    ) -> StructuredChatCompletionRequest:
        return StructuredChatCompletionRequest(
            model=model,
            messages=messages,
            response_format=StructuredResponseFormat(**response_format),
            **params,
        )
