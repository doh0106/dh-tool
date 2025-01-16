# src/app/infrastructure/llm/gpt.py
import inspect
from typing import Any

from openai import AsyncOpenAI
from openai.resources.chat.completions import Completions
from openai.types.completion import Completion

from .base import BaseLLM
from ..utils.response_parser import parse_openai_response


signature = inspect.signature(Completions.create)


class GPTModel(BaseLLM):

    def _get_allowed_params(self):
        self._allowed_generation_params.update(
            **{
                name: param.annotation
                for name, param in signature.parameters.items()
                if param.default
                is not inspect.Parameter.empty  # 기본값이 있는 파라미터만
            }
        )

    def _setup_client(self):
        self._client = AsyncOpenAI(api_key=self.config.api_key)

    async def generate(self, message: str, parsed=False, **kwargs: Any):
        generation_params = self.generation_params
        if kwargs:
            for k, v in kwargs.items():
                if k not in self._allowed_generation_params:
                    raise ValueError(f"Parameter '{k}' is not allowed.")
            generation_params.update(**kwargs)

        def gpt_request_format(message):
            return {
                "model": self.model,
                "messages": (
                    [
                        {"role": "system", "content": self.system_instruction},
                        {"role": "user", "content": message},
                    ]
                    if self.system_instruction
                    else [{"role": "user", "content": message}]
                ),
                **generation_params,
            }

        gpt_request = gpt_request_format(message)
        response = await self._client.chat.completions.create(**gpt_request)
        if parsed:
            return self.parse_response(response)
        return response

    @staticmethod
    def parse_response(response: Completion):
        return parse_openai_response(response)
