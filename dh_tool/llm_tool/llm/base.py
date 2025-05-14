# dh_tool/llm_tool/llm/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import inspect
from typing import Dict, Any, Optional


@dataclass
class LLMConfig:
    """LLM 설정"""

    model: str
    api_key: str
    system_instruction: Optional[str] = None
    generation_params: Dict[str, Any] = field(
        default_factory=lambda: {
            "temperature": 0.7,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "stop": None,
        }
    )

    def __post_init__(self) -> None:
        self.generation_params = {
            k: v for k, v in self.generation_params.items() if v is not None
        }


class BaseLLM(ABC):
    _allowed_generation_params = {}

    def __init__(self, config: LLMConfig) -> None:
        self.config = config
        self._client = None
        self._get_allowed_params()
        self._parse_config()
        self._setup_client()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        try:
            # Case 1: OpenAI - AsyncOpenAI client
            if hasattr(self._client, "close") and inspect.iscoroutinefunction(
                self._client.close
            ):
                await self._client.close()

            # Case 2: Google GenAI - aio path
            elif hasattr(self._client, "aio"):
                aio = self._client.aio
                httpx_client = getattr(
                    getattr(aio, "_api_client", None), "_async_httpx_client", None
                )
                if httpx_client and inspect.iscoroutinefunction(httpx_client.aclose):
                    await httpx_client.aclose()
            else:
                print("[BaseLLM] Client does not support async close. Skipping.")

        except Exception as e:
            print(f"[BaseLLM] Failed to close client: {e}")

    @abstractmethod
    def _get_allowed_params(self) -> None:
        pass

    @abstractmethod
    def _setup_client(self) -> None:
        pass

    @abstractmethod
    async def generate(self, message: str, parsed=True, **kwargs):
        pass

    @abstractmethod
    async def generate_stream(self, message: str, verbose=True, parsed=True, **kwargs):
        pass

    @abstractmethod
    async def parse_response(self):
        pass

    @property
    def is_ready(self) -> bool:
        """클라이언트 초기화 상태 확인"""
        return self._client is not None

    def _parse_config(self) -> None:
        """설정값을 파싱하여 프로퍼티 설정"""
        # 독립 속성 처리
        for key, value in self.config.__dict__.items():
            if key != "generation_params":
                setattr(self, f"_{key}", value)
        # generation_params 필터링
        self._generation_params = {}
        for key, value in self.config.generation_params.items():
            if key in self._allowed_generation_params:
                self._generation_params[key] = value
            else:
                print(f"Parameter '{key}' is not allowed.")
                print(f"Allowed parameters: {self._allowed_generation_params}")

    @property
    def generation_params(self) -> Dict[str, Any]:
        """현재 생성 파라미터 전체 조회"""
        return self._generation_params.copy()

    def get_generation_param(self, param_name: str, default: Any = None) -> Any:
        """특정 생성 파라미터 조회"""
        return self._generation_params.get(param_name, default)

    def update_generation_params(self, **params) -> None:
        """생성 파라미터 업데이트"""
        self._generation_params.update(params)

    def set_generation_param(self, param_name: str, value: Any) -> None:
        """특정 생성 파라미터 설정"""
        self._generation_params[param_name] = value

    @property
    def model(self) -> str:
        return self._model

    @property
    def system_instruction(self):
        return self._system_instruction
