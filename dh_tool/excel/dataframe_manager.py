import pandas as pd


class DataFrameManager:
    @staticmethod
    def filter(df, include=None, exclude=None, inplace=False):
        df_filtered = df.copy()

        if include:
            for col, condition in include.items():
                if isinstance(condition, tuple):
                    op, value = condition
                    if op == "in":
                        df_filtered = df_filtered[df_filtered[col].isin(value)]
                    elif op == "contains":
                        df_filtered = df_filtered[
                            df_filtered[col].astype(str).str.contains(value)
                        ]
                    else:
                        df_filtered = df_filtered.query(f"{col} {op} @value")
                else:
                    df_filtered = df_filtered[df_filtered[col] == condition]

        if exclude:
            for col, condition in exclude.items():
                if isinstance(condition, tuple):
                    op, value = condition
                    if op == "in":
                        df_filtered = df_filtered[~df_filtered[col].isin(value)]
                    elif op == "contains":
                        df_filtered = df_filtered[
                            ~df_filtered[col].astype(str).str.contains(value)
                        ]
                    else:
                        df_filtered = df_filtered.query(f"not ({col} {op} @value)")
                else:
                    df_filtered = df_filtered[df_filtered[col] != condition]

        if inplace:
            df[:] = df_filtered
            return None
        return df_filtered

    @staticmethod
    def aggregate(df, group_by, **aggregations):
        return df.groupby(group_by).agg(aggregations)

    @staticmethod
    def transform(df, func):
        return df.apply(func)
