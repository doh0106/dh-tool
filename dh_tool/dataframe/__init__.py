"""
dh_tool.dataframe

This package provides enhanced DataFrame functionality with Excel handling and visualization capabilities.
"""

__version__ = "0.1.0"

from .core.base import DataFrame
from .core.sheets import Sheets
from .handlers.dataframe_handler import DataFrameHandler
from .handlers.excel_handler import ExcelHandler
from .handlers.visualization_handler import VisualizationHandler

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
    "DataFrame",
    "Sheets",
    "DataFrameHandler",
    "ExcelHandler",
    "VisualizationHandler",
    "DEFAULT_WIDTH_CONFIG",
]
