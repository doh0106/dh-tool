from openai import OpenAI
import openai
from .stream import convert_stream_completion
from copy import deepcopy

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


class GPT:
    def __init__(self, api_key, model) -> None:
        self.client = OpenAI(api_key=api_key)
        openai.api_key = api_key
        self._instruction: str = None
        self._model: str = model
        self.model_emb = "text-embedding-3-large"
        self._params: dict = {
            "max_tokens": 1024,
            "temperature": 0,
            "seed": 0,
        }

    @property
    def params(self) -> dict:
        return self._params

    @params.setter
    def params(self, new_params: dict) -> None:
        if "max_tokens" in new_params:
            if new_params["max_tokens"] < 1:
                raise ValueError("max_tokens must be at least 1")
            elif new_params["max_tokens"] > 4096:
                raise ValueError("max_tokens must be at most 4096")
        self._params.update(new_params)

    @property
    def instruction(self) -> str:
        return self._instruction

    @instruction.setter
    def instruction(self, new_instruction: str) -> None:
        self._instruction = new_instruction

    @property
    def model(self) -> str:
        return self._model

    @model.setter
    def model(self, new_model: str) -> None:
        if new_model not in MODEL_PRICE:
            raise ValueError(f"model must in {list(MODEL_PRICE.keys())}")
        self._model = new_model

    def chat(self, comment, return_all=False):
        messages = [{"role": "user", "content": comment}]
        if self.instruction:
            messages.insert(0, {"role": "system", "content": self.instruction})

        completion = self.client.chat.completions.create(
            model=self.model, messages=messages, **self.params
        )
        if not return_all:
            return completion.choices[0].message.content
        else:
            return completion

    def stream(self, comment, verbose=True, return_all=False):
        messages = [{"role": "user", "content": comment}]
        if self.instruction:
            messages.insert(0, {"role": "system", "content": self.instruction})
        stream_params = deepcopy(self.params)
        stream_params.update({"stream_options": {"include_usage": True}})
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True,
            **stream_params,
        )
        completion = convert_stream_completion(stream, verbose)

        if not return_all:
            return completion.choices[0].message.content
        else:
            return completion

    def embed(self, texts, return_all=False):
        if isinstance(texts, str):
            texts = [texts]
        response = openai.embeddings.create(input=texts, model=self.model_emb)
        if not return_all:
            return [r.embedding for r in response.data]
        else:
            return response

    @staticmethod
    def cal_price(prompt_tokens, completion_tokens, model_name, exchange_rate=1400):

        if model_name in MODEL_PRICE:
            token_prices = MODEL_PRICE[model_name]
            return exchange_rate * (
                prompt_tokens * token_prices[0] + completion_tokens * token_prices[1]
            )
        print(f"{model_name} not in price dict")
        return 0
