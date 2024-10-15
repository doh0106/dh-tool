import pandas as pd
from ..handlers.excel_handler import ExcelHandler
from ..handlers.dataframe_handler import DataFrameHandler
from ..handlers.visualization_handler import VisualizationHandler


class DataFrame:
    def __init__(self, data: pd.DataFrame):
        self.df = data
        self.df_handler = DataFrameHandler(data)
        self.excel_handler = ExcelHandler()
        self.visualization_handler = VisualizationHandler()

        self.excel_handler.update(data)
        self.visualization_handler.update(data)

        self.excel_handler.on("data_updated", self._on_data_updated)
        self.visualization_handler.on("data_updated", self._on_data_updated)

    def _on_data_updated(self, new_df):
        self.df = new_df
        self.df_handler.update(new_df)

    def __getattr__(self, name):
        return getattr(self.df, name)

    def __getitem__(self, key):
        return self.df[key]

    # Excel 관련 메서드
    def save(self, filename):
        self.excel_handler.save(filename)

    def close(self):
        self.excel_handler.close()

    # DataFrame 처리 관련 메서드
    def select_rows(self, include=None, exclude=None, inplace=False):
        result = self.df_handler.select_rows(include, exclude, inplace)
        if inplace:
            self.df = self.df_handler.df
        return result

    def group_and_aggregate(self, group_by, inplace=False, **aggregations):
        """그룹화 및 집계"""
        result = self.df_handler.group_and_aggregate(group_by, inplace, **aggregations)
        if inplace:
            self.df = self.df_handler.df
        return result

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

    def apply_function(self, func, axis=0, inplace=False):
        """사용자 정의 함수를 데이터프레임에 적용"""
        result = self.df.apply(func, axis=axis)
        if inplace:
            self.df = result
            return None
        return result

    def to_excel(self, filename, **kwargs):
        """엑셀 파일로 저장 (추가 옵션 포함)"""
        self.excel_handler.save(filename, **kwargs)

    def style_excel(self, style_func):
        """엑셀 스타일 적용"""
        self.excel_handler.apply_style(style_func)

    def quick_plot(self, kind, x=None, y=None, **kwargs):
        """빠른 플롯 생성"""
        self.visualization_handler.quick_plot(kind, x, y, **kwargs)
