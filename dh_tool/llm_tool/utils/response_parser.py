# dh_tool/llm_tool/utils/response_parser.py
from box import Box
from openai.types.completion import Completion
from google.generativeai.types.generation_types import AsyncGenerateContentResponse


def parse_openai_response(response: Completion):
    """OpenAI GPT 응답 파싱"""
    text = response.choices[0].message.content
    usage = response.usage
    return Box({"text": text, "usage": usage})


def parse_gemini_response(response: AsyncGenerateContentResponse):
    """Gemini 응답 파싱"""
    text = response.candidates[0].content.parts[0].text
    usage = response.usage_metadata
    return Box({"text": text, "usage": usage})
