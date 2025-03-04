from typing import List

from dh_tool.llm_tool import *
from dh_tool.llm_tool.llm.gemini import GeminiModel

from .constants import *


def get_leader_model(gemini_key: str) -> GeminiModel:
    LEADER_GENERATION_PARAMS.update()
    leader = GeminiModel(
        LLMConfig(
            model="gemini-1.5-pro",
            api_key=gemini_key,
            system_instruction=LEADER_INSTCURTION,
            generation_params=LEADER_GENERATION_PARAMS,
        )
    )
    return leader


def make_follwer_instruction(roles: dict) -> str:
    specific_instruction = "\n\n".join([f"## {k}\n{v}" for k, v in roles.items()])
    return FOLLOWER_INSTRUCTION + "\n\n# 개별역할\n" + specific_instruction


def get_follower_models(gemini_key: str, roles: List[dict]) -> List[GeminiModel]:

    return [
        GeminiModel(
            LLMConfig(
                model="gemini-1.5-pro",
                api_key=gemini_key,
                system_instruction=make_follwer_instruction(role),
                generation_params=FOLLOWER_GENERATION_PARAMS,
            )
        )
        for role in roles
    ]


class CodeAnalysisAgent:
    def __init__(self, api_key: str, extra_info: str = None):
        self.api_key = api_key
        self.leader = get_leader_model(api_key)
        self.followers = None
        self.extra_info = extra_info
        self.result = None

    #
    async def run(self, code: str, roles: List[dict]):
        self.followers = get_follower_models(self.api_key, roles)
        response = self.leader.generate(code)
        responses = [follower.generate(response) for follower in self.followers]
        return responses
