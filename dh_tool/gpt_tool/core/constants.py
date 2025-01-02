import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

model_price_path = BASE_DIR / "data" / "model_price.csv"
price_data = pd.read_csv(model_price_path)
MODEL_PRICE = (
    price_data.set_index("model")[["prompt_tokens", "completion_tokens"]]
    .map(lambda x: float(x) / 1_000_000)  # Divide each value by 1,000,000
    .to_dict(orient="index")
)

STRUCTURED_OUTPUT_MODELS = [
    "gpt-4o-2024-08-06",
    "gpt-4o-mini",
    "gpt-4o-mini-2024-07-18",
    "gpt-4o-2024-11-20",
    "o1",
    "o1-2024-12-17",
    "o1-preview",
    "o1-preview-2024-09-12",
    "o1-mini",
    "o1-mini-2024-09-12",
]

MY_SYSTEM_PROMPT = (
    "당신은 질문을 깊이 있게 분석하고 단계적으로 사고하여 최적의 해결책을 제시하는 전문가입니다.\n"
    "\n"
    "분석 방법:\n"
    "1. chain of thought (단계적 사고)\n"
    "- 질문을 작은 단위로 분해하세요\n"
    "- 각 부분의 의미와 연관성을 파악하세요\n"
    "- 논리적 순서로 생각을 전개하세요\n"
    "\n"
    "2. zero-shot decomposition (즉각적 문제 분해)\n"
    "- 주어진 문제의 핵심 요소들을 파악하세요\n"
    "- 각 요소별 세부 고려사항을 도출하세요\n"
    "- 요소들 간의 상호작용을 고려하세요\n"
    "\n"
    "3. tree of thoughts (사고의 확장)\n"
    "- 다양한 관점에서 해결 방안을 탐색하세요\n"
    "- 각 방안의 장단점을 비교 분석하세요\n"
    "- 최적의 해결책으로 수렴하세요\n"
    "\n"
    "4. self-reflection (자기 검증)\n"
    "- 제시한 해결책의 실현 가능성을 검토하세요\n"
    "- 예상되는 문제점을 미리 파악하세요\n"
    "- 필요한 보완사항을 추가하세요\n"
    "\n"
    "응답은 반드시 다음 json 형식을 따라주세요:\n"
    "\n"
    "\n"
    "답변 시 준수사항:\n"
    "1. 모든 분석과 제안은 구체적이고 실행 가능해야 합니다\n"
    "2. 주관적 판단보다는 논리적 근거를 제시하세요\n"
    "3. 필요한 경우 예시나 참고자료를 포함하세요\n"
    "4. 불확실한 부분이 있다면 명시적으로 언급하세요\n"
    "5. 윤리적 고려사항이 있다면 반드시 포함하세요\n"
    "\n"
    "질문자의 상황과 맥락을 최대한 고려하여, 실질적인 도움이 되는 답변을 제공해주세요.\n"
)

MY_SYSTEM_RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "think_answer",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "intention": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "핵심 키워드나 주제",
                        },
                        "content": {
                            "type": "string",
                            "description": "해당 키워드/주제가 내포하는 실제 의도와 맥락",
                        },
                    },
                    "required": ["title", "content"],
                    "additionalProperties": False,
                },
                "thought_processes": {
                    "type": "array",
                    "description": "사고과정",
                    "items": {
                        "type": "object",
                        "properties": {
                            "situation_analysis": {
                                "type": "string",
                                "description": "현재 상황과 맥락의 상세분석",
                            },
                            "key_considerations": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "description": "고려사항 내용",
                                },
                            },
                        },
                        "required": ["situation_analysis", "key_considerations"],
                        "additionalProperties": False,
                    },
                },
                "extra_process": {
                    "type": "string",
                    "description": "유저 프롬프트에서 제시한 프로세스가 있다면 모든 과정(markdown형식 선호), 없다면 적지 않아도 좋음",
                },
                "answer": {
                    "type": "string",
                    "description": "질문과 너가 파악한 여러 단계의 의도를 합쳐서 최종적인 답변을 제공",
                },
            },
            "required": ["intention", "thought_processes", "extra_process", "answer"],
            "additionalProperties": False,
        },
    },
}
