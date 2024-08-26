import numpy as np 
from .observer import Observer


class DataFrameHandler(Observer):

    def __init__(self):
        super().__init__()
        self.df = None

    def update(self, dataframe):
        self.df = dataframe

    def filter_rows(self, include=None, exclude=None):
        def build_condition(column, condition, is_exclude=False):
            operator, value = condition
            if operator in ("==", "!=", "<", ">", "<=", ">="):
                if is_exclude:
                    return f"({column} {invert_operator(operator)} {repr(value)})"
                else:
                    return f"({column} {operator} {repr(value)})"
            elif operator == "in":
                if is_exclude:
                    return f"(~{column}.isin({value}))"
                else:
                    return f"({column}.isin({value}))"
            elif operator == "contains":
                if isinstance(self.df[column].iloc[0], (np.ndarray, list)):
                    # 리스트 또는 numpy 배열을 포함하는 경우
                    if is_exclude:
                        return self.df[column].apply(lambda y: not any(str(value) in str(item) for item in y))
                    else:
                        return self.df[column].apply(lambda y: any(str(value) in str(item) for item in y))
                else:
                    # 일반 문자열 열인 경우
                    if is_exclude:
                        return f"(~{column}.str.contains({repr(value)}))"
                    else:
                        return f"({column}.str.contains({repr(value)}))"
            else:
                raise ValueError(f"Unsupported operator: {operator}")

        def invert_operator(operator):
            return {"==": "!=", "!=": "==", "<": ">=", ">": "<=", "<=": ">", ">=": "<"}[operator]

        df_filtered = self.df

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

        return df_filtered




    def group_and_aggregate(self, group_by, **aggregations):
        """그룹화 및 집계"""
        return self.df.groupby(group_by).agg(aggregations)

    def fill_missing(self, strategy="mean", columns=None):
        """결측값 채우기"""
        if columns is None:
            columns = self.df.select_dtypes(include="number").columns
        else:
            columns = self.df[columns].select_dtypes(include="number").columns

        if strategy == "mean":
            self.df[columns] = self.df[columns].fillna(self.df[columns].mean())
        elif strategy == "median":
            self.df[columns] = self.df[columns].fillna(self.df[columns].median())
        elif strategy == "mode":
            self.df[columns] = self.df[columns].fillna(self.df[columns].mode().iloc[0])
        elif strategy == "ffill":
            self.df[columns] = self.df[columns].fillna(method="ffill")
        elif strategy == "bfill":
            self.df[columns] = self.df[columns].fillna(method="bfill")

        return self.df

    def normalize(self, columns=None):
        """정규화"""
        if columns is None:
            columns = self.df.select_dtypes(include="number").columns
        else:
            columns = self.df[columns].select_dtypes(include="number").columns

        self.df[columns] = (self.df[columns] - self.df[columns].mean()) / self.df[
            columns
        ].std()

        return self.df
