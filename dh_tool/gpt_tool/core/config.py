from typing import Dict, Any


class ModelConfig:
    def __init__(self, model: str, params: Dict[str, Any], system_prompt: str = ""):
        self.model = model
        self.params = params
        self.system_prompt = system_prompt

    def update_params(self, new_params: Dict[str, Any]) -> None:
        if "max_tokens" in new_params:
            if new_params["max_tokens"] < 1 or new_params["max_tokens"] > 128000:
                raise ValueError("max_tokens must be between 1 and 128000")
        self.params.update(new_params)
