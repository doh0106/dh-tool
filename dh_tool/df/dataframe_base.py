import pandas as pd

from .df_handler import DataFrameHandler
from .visual_handler import VisualizationHandler

class MyDataframeBase:
    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe
        self.df_handler = DataFrameHandler()
        self.visualization_handler = VisualizationHandler()
        self.df_handler.update(dataframe)
        self.visualization_handler.update(dataframe)

    def __getattribute__(self, name):
        try:
            df_handler = super().__getattribute__("df_handler")
            df = df_handler.df
            if hasattr(df, name):
                return getattr(df, name)
            return super().__getattribute__(name)
        except AttributeError:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            )

    def __getitem__(self, key):
        return self.df[key]

    # DataFrameHandler 메서드들에 대한 래퍼
    def filter_rows(self, include=None, exclude=None, inplace=False):
        """조건에 맞는 행 필터링. include와 exclude 조건을 구분"""
        if inplace:
            self.df = self.df_handler.filter_rows(include, exclude)
        else:
            return self.df_handler.filter_rows(include, exclude)

    def group_and_aggregate(self, group_by, inplace=False, **aggregations):
        """그룹화 및 집계"""
        if inplace:
            self.df = self.df_handler.group_and_aggregate(group_by, **aggregations)
        else:
            return self.df_handler.group_and_aggregate(group_by, **aggregations)

    def fill_missing(self, strategy="mean", columns=None, inplace=False):
        """결측값 채우기"""
        if inplace:
            self.df = self.df_handler.fill_missing(strategy, columns)
        else:
            return self.df_handler.fill_missing(strategy, columns)

    def normalize(self, columns=None, inplace=False):
        """정규화"""
        if inplace:
            self.df = self.df_handler.normalize(columns)
        else:
            return self.df_handler.normalize(columns)

    # VisualizationHandler 메서드들에 대한 래퍼
    def plot_histogram(self, column, bins=10, title=None):
        self.visualization_handler.plot_histogram(column, bins, title)

    def plot_boxplot(self, column, by=None, title=None):
        self.visualization_handler.plot_boxplot(column, by, title)

    def plot_scatter(self, x, y, hue=None, title=None):
        self.visualization_handler.plot_scatter(x, y, hue, title)

    def plot_heatmap(self, title=None):
        self.visualization_handler.plot_heatmap(title)

    def plot_bar(self, x, y, hue=None, title=None):
        self.visualization_handler.plot_bar(x, y, hue, title)

    def plot_line(self, x, y, hue=None, title=None):
        self.visualization_handler.plot_line(x, y, hue, title)