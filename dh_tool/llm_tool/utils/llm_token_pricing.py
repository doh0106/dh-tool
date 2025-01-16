from typing import Optional
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent


class TokenPriceCalculator:
    """
    LLM 토큰 가격 계산기
    """

    price_data = pd.read_csv(BASE_DIR.parent / "data/token_price_by_model.csv")
    _model_price_per_tokens = price_data.set_index("model")[
        ["input", "output", "input_name", "output_name"]
    ].to_dict(orient="index")

    @classmethod
    def calculate_price(
        cls, model: str, response_usage_data, exchange_rate=1450
    ) -> Optional[float]:
        """
        주어진 모델과 토큰 수로 가격을 계산합니다.

        Args:
            model (str): 모델 이름
            token_count (int): 토큰 수

        Returns:
            Optional[float]: 계산된 가격 (USD). 모델 정보가 없으면 None 반환.
        """
        denominator = 1_000_000
        price_per_token = cls._model_price_per_tokens.get(model)
        input_name = price_per_token.get("input_name")
        output_name = price_per_token.get("output_name")
        try:
            price = (
                (
                    getattr(response_usage_data, input_name) * price_per_token["input"]
                    + getattr(response_usage_data, output_name)
                    * price_per_token["output"]
                )
                / denominator
                * exchange_rate
            )
        except Exception as e:
            print(e)
            price = 0
        return price
