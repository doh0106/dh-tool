from typing import Dict, Any

import openai

from ..core.base import BaseChatModel
from ..core.config import ModelConfig
from ..services.chat_service import (
    SimpleChatModel,
    HistoryChatModel,
    StructuredChatModel,
    HistoryStructuredChatModel,
)
from ..services.async_chat_service import AsyncChatModel, AsyncStructuredChatModel


class ChatServiceFactory:
    @staticmethod
    def create_chat_service(
        gpt_type: str,
        api_key: str,
        model: str,
        params: Dict[str, Any],
        system_prompt: str = "",
        is_async: bool = False,
    ) -> BaseChatModel:
        if is_async:
            client = openai.AsyncOpenAI(api_key=api_key)
        else:
            client = openai.OpenAI(api_key=api_key)

        config = ModelConfig(model, params, system_prompt)

        if gpt_type == "simple":
            return (
                SimpleChatModel(client, config)
                if not is_async
                else AsyncChatModel(client, config)
            )
        elif gpt_type == "history":
            return HistoryChatModel(client, config)
        elif gpt_type == "structured":
            return (
                StructuredChatModel(client, config)
                if not is_async
                else AsyncStructuredChatModel(client, config)
            )
        elif gpt_type == "hs":
            return HistoryStructuredChatModel(client, config)
        else:
            raise ValueError(
                "Invalid GPT type. Choose 'simple', 'history', 'structured' or 'hs'."
            )


def create_chat_service(
    gpt_type: str,
    api_key: str,
    model: str,
    params: Dict[str, Any] = None,
    system_prompt: str = "",
    is_async: bool = False,
) -> BaseChatModel:
    """
    노트북 환경에서 쉽게 GPT 객체를 생성하는 함수

    :param gpt_type: GPT 유형 ('simple', 'history', 'structured', 'hs')
    :param api_key: OpenAI API 키
    :param model: 사용할 모델 이름
    :param params: 모델 파라미터 (기본값: None)
    :param system_prompt: 시스템 프롬프트 (기본값: "")
    :param is_async: 비동기 모델 사용 여부 (기본값: False)
    :return: 생성된 GPT 객체
    """
    if params is None:
        params = {}

    return ChatServiceFactory.create_chat_service(
        gpt_type, api_key, model, params, system_prompt, is_async
    )
