from pathlib import Path
import json

from dh_tool.llm_tool.llm.base import LLMConfig

FILE_DIR = Path(__file__).resolve().parent

with open(FILE_DIR / "instructions/leader_instruction.md", "rt", encoding="utf-8") as f:
    LEADER_INSTCURTION = f.read()

with open(
    FILE_DIR / "instructions/follower_instruction.md", "rt", encoding="utf-8"
) as f:
    FOLLOWER_INSTRUCTION = f.read()

with open(
    FILE_DIR / "instructions/leader_response_schema.json", "rt", encoding="utf-8"
) as f:
    LEADER_RESPONSE_SCHEMA = json.load(f)


LEADER_GENERATION_PARAMS = {
    "temperature": 0.1,
    "response_mime_type": "application/json",
    "response_schema": LEADER_RESPONSE_SCHEMA,
    "max_output_tokens": 2048,
}

FOLLOWER_GENERATION_PARAMS = {
    "temperature": 0.7,
    "max_output_tokens": 4096,
}
