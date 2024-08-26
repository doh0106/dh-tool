import pandas as pd

from .excel_handler import ExcelHandler
from .dataframe_base import MyDataframeBase


class MyDataframe(MyDataframeBase):
    def __init__(self, dataframe: pd.DataFrame):
        super().__init__(dataframe)
        self.excel_handler = ExcelHandler()
        self.excel_handler.create_sheet(dataframe)

    @property
    def sheet_names(self):
        return self.excel_handler.list_sheets()

    @property
    def curruent_sheet(self):
        return self.excel_handler.get_active_sheet()

    def save(self, filename):
        """엑셀 파일 저장"""
        self.excel_handler.save(filename)

    def close(self):
        """엑셀 파일 닫기"""
        self.excel_handler.close()

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
