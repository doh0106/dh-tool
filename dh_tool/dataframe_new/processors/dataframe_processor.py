from typing import Any

import numpy as np
import pandas as pd


class DataFrameProcessor:
    def __init__(self, dataframe: pd.DataFrame) -> None:
        self._df = dataframe

    @property
    def df(self) -> pd.DataFrame:
        return self._df

    def update(self, dataframe: pd.DataFrame) -> None:
        self._df = dataframe

    def select_rows(
        self, include=None, exclude=None, inplace=False
    ) -> None | pd.DataFrame | Any:
        def build_condition(column, condition, is_exclude=False):
            # 컬럼 존재 여부 먼저 확인
            if column not in self.df.columns:
                raise KeyError(f"Column '{column}' not found in DataFrame")

            operator, value = condition
            if operator in ("==", "!=", "<", ">", "<=", ">="):
                if is_exclude:
                    return f"({self.df[column].name} {invert_operator(operator)} {repr(value)})"
                else:
                    return f"({self.df[column].name} {operator} {repr(value)})"
            elif operator == "in":
                if is_exclude:
                    return f"(~{self.df[column].name}.isin({value}))"
                else:
                    return f"({self.df[column].name}.isin({value}))"
            elif operator == "contains":
                if isinstance(self.df[column].iloc[0], (np.ndarray, list)):
                    # 리스트 또는 numpy 배열을 포함하는 경우
                    if is_exclude:
                        return self.df[column].apply(
                            lambda y: not any(str(value) in str(item) for item in y)
                        )
                    else:
                        return self.df[column].apply(
                            lambda y: any(str(value) in str(item) for item in y)
                        )
                else:
                    # 일반 문자열 열인 경우
                    if is_exclude:
                        return f"(~{self.df[column].name}.str.contains({repr(value)}))"
                    else:
                        return f"({self.df[column].name}.str.contains({repr(value)}))"
            else:
                raise ValueError(f"Unsupported operator: {operator}")

        def invert_operator(operator):
            return {"==": "!=", "!=": "==", "<": ">=", ">": "<=", "<=": ">", ">=": "<"}[
                operator
            ]

        df_filtered = self.df.copy()

        if include:
            for col, val in include.items():
                if isinstance(val, tuple):
                    condition = build_condition(col, val)
                    if isinstance(condition, str):
                        df_filtered = df_filtered.query(condition)
                    else:
                        df_filtered = df_filtered[condition]
                else:
                    df_filtered = df_filtered[df_filtered[col] == val]

        if exclude:
            for col, val in exclude.items():
                if isinstance(val, tuple):
                    condition = build_condition(col, val, is_exclude=True)
                    if isinstance(condition, str):
                        df_filtered = df_filtered.query(condition)
                    else:
                        df_filtered = df_filtered[condition]
                else:
                    df_filtered = df_filtered[df_filtered[col] != val]

        if inplace:
            self.df = df_filtered
            return None
        return df_filtered
