from .base import DataFrame
from ..handlers.excel_handler import ExcelHandler
import numpy as np
import pandas as pd


class Sheets(DataFrame):
    def __init__(self, data):
        super().__init__(data)
        self.excel_handler = ExcelHandler()
        self.excel_handler.update(data)

    @property
    def sheet_names(self):
        return self.excel_handler.list_sheets()

    @property
    def current_sheet(self):
        return self.excel_handler.get_active_sheet()

    def save(self, filename):
        """엑셀 파일 저장"""
        self.excel_handler.update(self.df)  # 현재 데이터프레임으로 업데이트
        self.excel_handler.save(filename)

    def close(self):
        """엑셀 파일 닫기"""
        self.excel_handler.close()

    def create_sheet(self, dataframe, title=None):
        is_success = self.excel_handler.create_sheet(dataframe, title)
        if is_success:
            self.select_sheet(title)

    def select_sheet(self, title):
        self.df = self.excel_handler.select_sheet(title)
        self.df_handler.update(self.df)
        self.visualization_handler.update(self.df)

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

    def copy_sheet(self, source_sheet, target_sheet):
        """시트 복사"""
        self.excel_handler.copy_sheet(source_sheet, target_sheet)

    def rename_sheet(self, old_name, new_name):
        """시트 이름 변경"""
        self.excel_handler.rename_sheet(old_name, new_name)

    def merge_sheets(self, sheet_names, merged_sheet_name):
        """여러 시트 병합"""
        self.excel_handler.merge_sheets(sheet_names, merged_sheet_name)

    def apply_formula_to_column(self, sheet_name, column, formula):
        """특정 열에 수식 적용"""
        self.excel_handler.apply_formula_to_column(sheet_name, column, formula)
