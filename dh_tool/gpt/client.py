import openai
from openai import OpenAI


class OpenAIClient:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        openai.api_key = api_key
