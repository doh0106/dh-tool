import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, Union, List


class DataFrameHandler:
    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe

    def select_rows(self, include=None, exclude=None, inplace=False):
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

    def group_and_aggregate(
        self, group_by: Union[str, list], inplace: bool = False, **aggregations
    ) -> Union[pd.DataFrame, None]:
        """
        그룹화 및 집계

        :param group_by: 그룹화할 열 이름 또는 열 이름 리스트
        :param inplace: True면 원본 데이터프레임을 변경, False면 새로운 데이터프레임 반환
        :param aggregations: 집계 함수 (예: A='mean', B='sum')
        :return: 집계된 데이터프레임 또는 None (inplace=True인 경우)
        """
        result = self.df.groupby(group_by).agg(aggregations)

        if inplace:
            self.df = result
            return None
        return result

    def fill_missing(
        self,
        strategy: str = "mean",
        columns: Optional[list] = None,
        inplace: bool = False,
    ) -> Union[pd.DataFrame, None]:
        """
        결측값 채우기

        :param strategy: 채우기 전략 ('mean', 'median', 'mode', 'ffill', 'bfill')
        :param columns: 처리할 열 목록 (None이면 모든 열)
        :param inplace: True면 원본 데이터프레임을 변경, False면 새로운 데이터프레임 반환
        :return: 결측값이 채워진 데이터프레임 또는 None (inplace=True인 경우)
        """
        df = self.df.copy()
        columns = columns or df.columns

        for col in columns:
            if strategy == "mean":
                df[col].fillna(df[col].mean(), inplace=True)
            elif strategy == "median":
                df[col].fillna(df[col].median(), inplace=True)
            elif strategy == "mode":
                df[col].fillna(df[col].mode()[0], inplace=True)
            elif strategy == "ffill":
                df[col].fillna(method="ffill", inplace=True)
            elif strategy == "bfill":
                df[col].fillna(method="bfill", inplace=True)

        if inplace:
            self.df = df
            return None
        return df

    def normalize(
        self, columns: Optional[list] = None, inplace: bool = False
    ) -> Union[pd.DataFrame, None]:
        """
        지정된 열 정규화 (0-1 범위로 스케일링)

        :param columns: 정규화할 열 목록 (None이면 모든 숫자형 열)
        :param inplace: True면 원본 데이터프레임을 변경, False면 새로운 데이터프레임 반환
        :return: 정규화된 데이터프레임 또는 None (inplace=True인 경우)
        """
        df = self.df.copy()
        columns = columns or df.select_dtypes(include=[np.number]).columns

        for col in columns:
            df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())

        if inplace:
            self.df = df
            return None
        return df

    def get_dataframe(self) -> pd.DataFrame:
        """
        현재 데이터프레임 반환
        """
        return self.df

    def apply_function(self, func, axis=0):
        """사용자 정의 함수를 데이터프레임에 적용"""
        return self.df.apply(func, axis=axis)

    def pivot_table(self, values, index, columns, aggfunc="mean"):
        """피벗 테이블 생성"""
        return pd.pivot_table(
            self.df, values=values, index=index, columns=columns, aggfunc=aggfunc
        )

    def melt(self, id_vars, value_vars, var_name=None, value_name="value"):
        """데이터프레임 melting"""
        return pd.melt(
            self.df,
            id_vars=id_vars,
            value_vars=value_vars,
            var_name=var_name,
            value_name=value_name,
        )

    def drop_duplicates(self, subset=None, keep="first", inplace=False):
        """중복 행 제거"""
        df_copy = self.df.copy()

        # 리스트 타입 컬럼이 있는 경우 문자열로 변환
        if subset is None:
            list_columns = [
                col
                for col in df_copy.columns
                if df_copy[col].apply(lambda x: isinstance(x, list)).any()
            ]
            for col in list_columns:
                df_copy[col] = df_copy[col].apply(str)
        else:
            # subset에 지정된 컬럼만 확인
            list_columns = [
                col
                for col in subset
                if col in df_copy.columns
                and df_copy[col].apply(lambda x: isinstance(x, list)).any()
            ]
            for col in list_columns:
                df_copy[col] = df_copy[col].apply(str)

        result = df_copy.drop_duplicates(subset=subset, keep=keep)

        if inplace:
            self.df = result
            return None
        return result

    def to_datetime(
        self, column: str, format: Optional[str] = None, inplace: bool = False
    ):
        """문자열 열을 datetime으로 변환"""
        if inplace:
            self.df[column] = pd.to_datetime(self.df[column], format=format)
            return None
        return pd.to_datetime(self.df[column], format=format)

    def update(self, dataframe: pd.DataFrame):
        """데이터프레임 업데이트"""
        self.df = dataframe
