from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


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
        self._generation_params = {
            k: v
            for k, v in self.config.generation_params.items()
            if k in self._allowed_generation_params
        }

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
