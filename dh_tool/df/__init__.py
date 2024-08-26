from .excel_handler import ExcelHandler
from .df_handler import DataFrameHandler
from .visual_handler import VisualizationHandler
from .dataframe_base import MyDataframeBase as mdb
from .dataframe import MyDataframe as md
from .sheets import Sheets

DEFAULT_WIDTH_CONFIG = {
    "Comments": 90,
    "BestSentence1": 20,
    "BestSentence2": 20,
    "FeedBack": 40,
    "timestamp": 20,
    "level": 10,
    "topic": 20,
    "message": 40,
    "description": 60,
    "traceback": 80,
}


__all__ = [
    "ExcelHandler",
    "DataFrameHandler",
    "VisualizationHandler",
    "mdb",
    "md",
    "Sheets",
    "DEFAULT_WIDTH_CONFIG",
]
