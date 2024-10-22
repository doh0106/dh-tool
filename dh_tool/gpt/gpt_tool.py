from openai import OpenAI
import openai
from .stream import process_and_convert_stream
from .structured import create_structured_body
from copy import deepcopy
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Union
import json

MODEL_PRICE = {
    "gpt-3.5-turbo-0125": [0.5 / 1000000, 1.5 / 1000000],
    "gpt-3.5-turbo-0301": [1.5 / 1000000, 2 / 1000000],
    "gpt-4": [30 / 1000000, 60 / 1000000],
    "gpt-4-0125-preview": [10 / 1000000, 30 / 1000000],
    "gpt-4o": [5 / 1000000, 15 / 1000000],
    "gpt-4o-2024-05-13": [5 / 1000000, 15 / 1000000],
    "gpt-4o-2024-08-06": [2.5 / 1000000, 10 / 1000000],
    "gpt-4o-mini": [0.15 / 1000000, 0.6 / 1000000],
    "gpt-4o-mini-2024-07-18": [0.15 / 1000000, 0.6 / 1000000],
}

STRUCTURED_OUTPUT_MODELS = [
    "gpt-4-1106-preview",
    "gpt-4-0125-preview",
    "gpt-4-turbo-preview",
    "gpt-4o-mini",
    "gpt-4o-mini-2024-07-18",
]


class OpenAIClient:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        openai.api_key = api_key


class ModelConfig:
    def __init__(self, model: str, params: Dict[str, Any], system_prompt: str = ""):
        self.model = model
        self.params = params
        self.system_prompt = system_prompt

    def update_params(self, new_params: Dict[str, Any]) -> None:
        if "max_tokens" in new_params:
            if new_params["max_tokens"] < 1 or new_params["max_tokens"] > 4096:
                raise ValueError("max_tokens must be between 1 and 4096")
        self.params.update(new_params)


class MessageHandler:
    @staticmethod
    def create_messages(system_prompt: str, user_message: str) -> List[Dict[str, str]]:
        messages = [{"role": "user", "content": user_message}]
        if system_prompt:
            messages.insert(0, {"role": "system", "content": system_prompt})
        return messages


class BaseGPT(ABC):
    def __init__(self, client: OpenAIClient, config: ModelConfig):
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


class SimpleGPT(BaseGPT):
    def __init__(self, client: OpenAIClient, config: ModelConfig):
        super().__init__(client, config)

    def chat(self, comment: str, return_all: bool = False):
        messages = self.message_handler.create_messages(
            self.config.system_prompt, comment
        )
        completion = self.client.client.chat.completions.create(
            model=self.config.model, messages=messages, **self.config.params
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


class HistoryGPT(BaseGPT):
    def __init__(self, client: OpenAIClient, config: ModelConfig):
        super().__init__(client, config)
        self.history: List[Dict[str, str]] = []
        self.message_handler = MessageHandler()

    def chat(self, comment: str, return_all: bool = False):
        messages = self.history + self.message_handler.create_messages(
            self.config.system_prompt, comment
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


class StructuredGPT(BaseGPT):
    def __init__(self, client: OpenAIClient, config: ModelConfig):
        super().__init__(client, config)
        if self.config.model not in STRUCTURED_OUTPUT_MODELS:
            raise ValueError(
                f"Model {self.config.model} does not support structured output"
            )

    def chat(
        self, content: str, response_format: Dict[str, Any], return_all: bool = False
    ):
        messages = self.message_handler.create_messages(
            self.config.system_prompt, content
        )
        body = create_structured_body(
            messages, response_format, model=self.config.model, **self.config.params
        )
        completion = self.client.client.chat.completions.create(**body)

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
        messages = self.message_handler.create_messages(
            self.config.system_prompt, content
        )
        body = create_structured_body(
            messages, response_format, model=self.config.model, **self.config.params
        )
        body["stream"] = True
        stream = self.client.client.chat.completions.create(**body)
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
) -> BaseGPT:
    """
    노트북 환경에서 쉽게 GPT 객체를 생성하는 함수

    :param gpt_type: GPT 유형 ('simple_gpt', 'history_gpt', 'structured_gpt')
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
    ) -> BaseGPT:
        client = OpenAIClient(api_key)
        config = ModelConfig(model, params, system_prompt)
        if gpt_type == "simple_gpt":
            return SimpleGPT(client, config)
        elif gpt_type == "history_gpt":
            return HistoryGPT(client, config)
        elif gpt_type == "structured_gpt":
            return StructuredGPT(client, config)
        else:
            raise ValueError(
                "Invalid GPT type. Choose 'simple_gpt', 'history_gpt', or 'structured_gpt'."
            )
