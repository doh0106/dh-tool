from abc import ABC, abstractmethod
from box import Box
from typing import AsyncIterator, Dict, Any
import itertools

from ..utils.response_parser import parse_gemini_response, parse_openai_response


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


# class GeminiStreamProcessor:
#     @staticmethod
#     async def process_stream(
#         stream_output: AsyncIterator[Dict[str, Any]], verbose: bool
#     ) -> Box:
#         collected_text = ""  # 최종 합쳐질 텍스트
#         last_candidate = None  # 마지막 candidate 저장
#         usage_metadata = {
#             "prompt_token_count": 0,
#             "total_token_count": 0,
#             "cached_content_token_count": 0,
#             "candidates_token_count": 0,
#         }

#         async for chunk in stream_output:
#             # 텍스트 추출 및 합치기
#             chunk = chunk.to_dict()
#             text = chunk["candidates"][0]["content"]["parts"][0]["text"]
#             collected_text += text
#             print(text, end="", flush=True) if verbose else None

#             last_candidate = chunk["candidates"][0]  # 마지막 응답을 저장

#             # usage_metadata 업데이트 (토큰 개수 합산)
#             for key in usage_metadata.keys():
#                 if key in chunk["usage_metadata"]:
#                     usage_metadata[key] += chunk["usage_metadata"][key]

#         # 최종 후보자(candidates) 생성
#         merged_candidate = {
#             "content": {"parts": [{"text": collected_text}], "role": "model"},
#             "finish_reason": last_candidate["finish_reason"],
#             "safety_ratings": last_candidate["safety_ratings"],
#             "token_count": last_candidate["token_count"],
#             "grounding_attributions": last_candidate["grounding_attributions"],
#             "avg_logprobs": last_candidate["avg_logprobs"],
#         }

#         # 최종 응답 객체 구성
#         complete_response = {
#             "candidates": [merged_candidate],
#             "usage_metadata": usage_metadata,
#         }

#         return Box(complete_response)  # Box로 감싸서 반환


class GeminiStreamProcessor:
    @staticmethod
    async def process_stream(
        stream_output: AsyncIterator[Dict[str, Any]], verbose: bool
    ) -> Box:
        collected_text = ""  # 최종 합쳐질 텍스트
        last_candidate = None  # 마지막 candidate 저장
        usage_metadata = {
            "prompt_token_count": 0,
            "total_token_count": 0,
            "cached_content_token_count": 0,
            "candidates_token_count": 0,
        }
        combined_safety_ratings = []  # safety_ratings을 누적 저장
        combined_grounding_attributions = []  # grounding_attributions 누적 저장
        total_token_count = 0  # token_count 누적
        avg_logprobs = []  # logprobs를 모아 평균 계산

        async for chunk in stream_output:
            chunk = chunk.to_dict()
            text = chunk["candidates"][0]["content"]["parts"][0]["text"]
            collected_text += text
            print(text, end="", flush=True) if verbose else None

            last_candidate = chunk["candidates"][0]  # 마지막 응답을 저장

            # usage_metadata 업데이트 (토큰 개수 합산)
            for key in usage_metadata.keys():
                if key in chunk["usage_metadata"]:
                    usage_metadata[key] += chunk["usage_metadata"][key]

            # safety_ratings 합치기 (리스트 병합)
            if "safety_ratings" in last_candidate:
                combined_safety_ratings.extend(last_candidate["safety_ratings"])

            # grounding_attributions 합치기 (리스트 병합)
            if "grounding_attributions" in last_candidate:
                combined_grounding_attributions.extend(
                    last_candidate["grounding_attributions"]
                )

            # token_count 합산
            total_token_count += last_candidate.get("token_count", 0)

            # avg_logprobs 값 추가 (평균 계산을 위해 리스트로 저장)
            if "avg_logprobs" in last_candidate:
                avg_logprobs.append(last_candidate["avg_logprobs"])

        # avg_logprobs 평균 계산
        avg_logprobs_value = (
            sum(avg_logprobs) / len(avg_logprobs) if avg_logprobs else 0.0
        )

        # 최종 후보자(candidates) 생성
        merged_candidate = {
            "content": {"parts": [{"text": collected_text}], "role": "model"},
            "finish_reason": last_candidate["finish_reason"],
            "safety_ratings": combined_safety_ratings,
            "token_count": total_token_count,
            "grounding_attributions": combined_grounding_attributions,
            "avg_logprobs": avg_logprobs_value,
        }

        # 최종 응답 객체 생성
        complete_response = {
            "candidates": [merged_candidate],
            "usage_metadata": usage_metadata,
        }

        return Box(complete_response)  # Box 객체로 반환
