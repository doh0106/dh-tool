from abc import ABC, abstractmethod

from .client import OpenAIClient
from .config import ModelConfig
from .constants import MODEL_PRICE
from .utils import MessageHandler


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
