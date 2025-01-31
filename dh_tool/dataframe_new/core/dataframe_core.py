# dh_tool/dataframe_new/core/dataframe_core.py

import pandas as pd

from ..utils.event_bus import EventBus

# from ..processors import dataframe_processor, excel_exporter, data_visualizer
from ..processors import DataFrameProcessor, ExcelManager  # , DataVisualizer


class DataFrameCore:
    def __init__(self, dataframe: pd.DataFrame):
        super().__init__()
        self._df = dataframe
        self.event_bus = EventBus()
        self.dataframe_processor = DataFrameProcessor(dataframe)
        self.excel_manager = ExcelManager(dataframe)
        # self.data_visualizer = DataVisualizer(dataframe)
        # self._processor = {
        #     "processor": self.processor,
        #     "excel_exporter": self.excel_exporter,
        #     # "visualizer": self.data_visualizer,
        # }
        self.event_bus.register("data_updated", self.dataframe_processor.update)
        self.event_bus.register("data_updated", self.excel_manager.update)
        # self.event_bus.register("data_updated", self.visualizer.update)

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, data):
        self._df = data
        self.event_bus.emit("data_updated", self.df)

    def select_rows(self, include=None, exclude=None, inplace=False):
        new_df = self.dataframe_processor.select_rows(include, exclude, inplace)
        if inplace:
            self._df = new_df
        else:
            return new_df

    def save(self, filename):
        self.excel_manager.save(filename)

    def create_sheet(self, title="Sheet"):
        return self.excel_manager.create_sheet(title)

    def select_sheet(self, title):
        return self.excel_manager.select_sheet(title)

    def enable_autowrap(self):
        self.excel_manager.enable_autowrap()

    def set_column_width(self, width):
        self.excel_manager.set_column_width(width)
