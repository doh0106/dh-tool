from .df_handler import DataFrameHandler
from .excel_handler import ExcelHandler
from .visual_handler import VisualizationHandler
from .observer import Subject


def notify_observers(method):
    def wrapper(self, *args, **kwargs):
        result = method(self, *args, **kwargs)
        self.notify(self.df)
        return result

    return wrapper


class Sheets(Subject):
    def __init__(self):
        super().__init__()
        self.df = None
        self.df_handler = DataFrameHandler()
        self.excel_handler = ExcelHandler()
        self.visualization_handler = VisualizationHandler()

        self.attach(self.df_handler)
        self.attach(self.excel_handler)
        self.attach(self.visualization_handler)

    @property
    def sheet_names(self):
        return self.excel_handler.list_sheets()

    @property
    def curruent_sheet(self):
        return self.excel_handler.get_active_sheet()

    def notify_observers_handlers(self):
        """데이터프레임 변경 시 핸들러 간 동기화"""
        self.visualization_handler.df = self.df_handler.get_dataframe()
        self.excel_handler.df = self.df_handler.get_dataframe()
        self.excel_handler._update_worksheet()

    def save(self, filename):
        """엑셀 파일 저장"""
        self.excel_handler.save(filename)

    def close(self):
        """엑셀 파일 닫기"""
        self.excel_handler.close()

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
    @notify_observers
    def filter_rows(self, include=None, exclude=None, inplace=False):
        """조건에 맞는 행 필터링. include와 exclude 조건을 구분"""
        if inplace:
            self.df = self.df_handler.filter_rows(include, exclude)
        else:
            return self.df_handler.filter_rows(include, exclude)

    @notify_observers
    def group_and_aggregate(self, group_by, inplace=False, **aggregations):
        """그룹화 및 집계"""
        if inplace:
            self.df = self.df_handler.group_and_aggregate(group_by, **aggregations)
        else:
            return self.df_handler.group_and_aggregate(group_by, **aggregations)

    @notify_observers
    def fill_missing(self, strategy="mean", columns=None, inplace=False):
        """결측값 채우기"""
        if inplace:
            self.df = self.df_handler.fill_missing(strategy, columns)
        else:
            return self.df_handler.fill_missing(strategy, columns)

    @notify_observers
    def normalize(self, columns=None, inplace=False):
        """정규화"""
        if inplace:
            self.df = self.df_handler.normalize(columns)
        else:
            return self.df_handler.normalize(columns)

    # ExcelHandler 메서드들에 대한 래퍼
    def create_sheet(self, dataframe, title=None):
        is_sucess = self.excel_handler.create_sheet(dataframe, title)
        if is_sucess:
            self.select_sheet(title)

    @notify_observers
    def select_sheet(self, title):
        self.df = self.excel_handler.select_sheet(title)

    def remove_sheet(self, title):
        self.excel_handler.remove_sheet(title)

    def set_column_width(self, **kwargs):
        """컬럼 너비 설정"""
        self.excel_handler.set_column_width(**kwargs)

    def freeze_first_row(self):
        """첫 번째 행 고정"""
        self.excel_handler.freeze_first_row()

    def enable_autowrap(self):
        """자동 줄 바꿈 활성화"""
        self.excel_handler.enable_autowrap()

    def add_hyperlink(self, cell, url, display=None):
        """셀에 하이퍼링크 추가"""
        self.excel_handler.add_hyperlink(cell, url, display)

    def add_hyperlinks_to_column(self, column_name, urls, display_texts=None):
        """컬럼에 있는 각 셀에 하이퍼링크 추가"""
        self.excel_handler.add_hyperlinks_to_column(column_name, urls, display_texts)

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
