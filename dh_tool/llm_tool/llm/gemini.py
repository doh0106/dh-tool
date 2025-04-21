# dh_tool/llm_tool/llm/gemini.py
from typing import Any

import google.genai as genai

from google.genai.types import GenerateContentConfig, GenerateContentResponse


from .base import BaseLLM
from ..utils.response_parser import parse_gemini_response
from ..utils.stream_processor import GeminiStreamProcessor


class GeminiModel(BaseLLM):

    def _get_allowed_params(self):
        self._allowed_generation_params = {
            i for i in GenerateContentConfig.model_fields
        }

    def _setup_client(self):
        self._client = genai.Client(
            api_key=self.config.api_key,
        )

    async def generate(self, message: str, parsed=True, **kwargs: Any):
        generation_params = self.generation_params
        if kwargs:
            for k, v in kwargs.items():
                if k not in self._allowed_generation_params:
                    raise ValueError(f"Parameter '{k}' is not allowed.")
            generation_params.update(**kwargs)

        if self.config.system_instruction:
            generation_params["system_instruction"] = self.config.system_instruction

        response = await self._client.aio.models.generate_content(
            model=self.config.model,
            contents=message,
            config=GenerateContentConfig(**generation_params),
        )

        if parsed:
            return self.parse_response(response)
        return response

    async def generate_stream(
        self, message: str, vebose=True, parsed=True, **kwargs: Any
    ):
        generation_params = self.generation_params
        if kwargs:
            for k, v in kwargs.items():
                if k not in self._allowed_generation_params:
                    raise ValueError(f"Parameter '{k}' is not allowed.")
            generation_params.update(**kwargs)

        if self.config.system_instruction:
            generation_params["system_instruction"] = self.config.system_instruction

        stream = await self._client.aio.models.generate_content_stream(
            model=self.config.model,
            contents=message,
            config=GenerateContentConfig(**generation_params),
        )

        response = await GeminiStreamProcessor.process_stream(stream, verbose=vebose)
        if parsed:
            return self.parse_response(response)
        return response

    @staticmethod
    def parse_response(response: GenerateContentResponse):
        return parse_gemini_response(response)
