from abc import ABC, abstractmethod
from box import Box
from typing import AsyncIterator, Dict, Any
import itertools

# from ..utils.response_parser import parse_gemini_response, parse_openai_response


class AsyncStreamProcessorInterface(ABC):
    @staticmethod
    @abstractmethod
    async def process_stream(
        stream_output: AsyncIterator[Dict[str, Any]], verbose: bool
    ) -> Box:
        pass


class GPTStreamProcessor(AsyncStreamProcessorInterface):

    @staticmethod
    async def process_stream(
        stream_output: AsyncIterator[Dict[str, Any]], verbose: bool
    ) -> Box:
        collected_messages = []
        full_response = []
        usage_info = None
        model = None
        created = None

        async for chunk in stream_output:
            full_response.append(chunk)
            if chunk.choices:
                chunk_message = chunk.choices[0].delta.content
                if chunk_message:
                    collected_messages.append(chunk_message)
                    if verbose:
                        print(chunk_message, end="", flush=True)
            else:
                usage_info = chunk.usage
                model = chunk.model
                created = chunk.created

        full_message = "".join(collected_messages)

        complete_response = {
            "id": full_response[0].id,
            "object": full_response[0].object,
            "created": created,
            "model": model,
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": full_message,
                    },
                    "finish_reason": "stop",
                    "index": 0,
                }
            ],
            "usage": usage_info,
        }
        return Box(complete_response)


from typing import AsyncIterator, Dict, Any
from box import Box


from google.genai.types import GenerateContentResponse


class GeminiStreamProcessor:
    @staticmethod
    async def process_stream(stream_output: AsyncIterator[Any], verbose: bool) -> Box:
        valid_fields = set(GenerateContentResponse.model_fields.keys())

        collected_text = ""
        last_candidate = None
        last_usage_metadata = {}
        combined_values = {field: [] for field in valid_fields if field != "content"}

        async for chunk in stream_output:
            if not isinstance(chunk, Box):
                chunk = Box(chunk)

            text = getattr(chunk.candidates[0].content.parts[0], "text", "")
            collected_text += text
            if verbose:
                print(text, end="", flush=True)

            last_candidate = chunk.candidates[0]
            last_usage_metadata = getattr(chunk, "usage_metadata", {})

            for field in valid_fields:
                if field == "content":
                    continue
                value = getattr(last_candidate, field, None)
                if value is not None:
                    if isinstance(value, list):
                        combined_values[field].extend(value)
                    else:
                        combined_values[field].append(value)

        merged_candidate = {
            "content": {"parts": [{"text": collected_text}], "role": "model"}
        }

        for field, values in combined_values.items():
            if values:
                if field == "avg_logprobs":
                    merged_candidate[field] = sum(values) / len(values)
                elif field == "token_count":
                    merged_candidate[field] = sum(values)
                else:
                    merged_candidate[field] = values

        complete_response = {
            "candidates": [merged_candidate],
            "usage_metadata": last_usage_metadata,
            "text": collected_text,
        }

        return Box(complete_response)
