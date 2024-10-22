import os
import json
import numpy as np
import pickle
import pandas as pd
import yaml
import scipy.io
import sqlite3
import cv2
from PIL import Image
import librosa
from abc import ABC, abstractmethod
import xml.etree.ElementTree as ET


def exception_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"An error occurred in {func.__name__}: {str(e)}")
            return None

    return wrapper


class FileHandler(ABC):
    @abstractmethod
    def load(self, path: str, **kwargs):
        pass

    @abstractmethod
    def save(self, data, path: str, **kwargs):
        pass


class TextFileHandler(FileHandler):
    @exception_handler
    def load(self, path: str, **kwargs):
        with open(path, "r", **kwargs) as file:
            return file.read()

    @exception_handler
    def save(self, data, path: str, **kwargs):
        with open(path, "w", **kwargs) as file:
            file.write(data)


class JsonFileHandler(FileHandler):
    @exception_handler
    def load(self, path: str, **kwargs):
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    @exception_handler
    def save(self, data, path: str, **kwargs):
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, **kwargs)


class CsvFileHandler(FileHandler):
    @exception_handler
    def load(self, path: str, **kwargs):
        return pd.read_csv(path, **kwargs)

    @exception_handler
    def save(self, data, path: str, **kwargs):
        data.to_csv(path, **kwargs)


class ExcelFileHandler(FileHandler):
    @exception_handler
    def load(self, path: str, **kwargs):
        return pd.read_excel(path, **kwargs)

    @exception_handler
    def save(self, data, path: str, **kwargs):
        data.to_excel(path, **kwargs)


class ParquetFileHandler(FileHandler):
    @exception_handler
    def load(self, path: str, **kwargs):
        return pd.read_parquet(path, **kwargs)

    @exception_handler
    def save(self, data, path: str, **kwargs):
        data.to_parquet(path, **kwargs)


class PickleFileHandler(FileHandler):
    @exception_handler
    def load(self, path: str, **kwargs):
        with open(path, "rb") as file:
            return pickle.load(file)

    @exception_handler
    def save(self, data, path: str, **kwargs):
        with open(path, "wb") as file:
            pickle.dump(data, file, **kwargs)


class NpzFileHandler(FileHandler):
    @exception_handler
    def load(self, path: str, **kwargs):
        return np.load(path, **kwargs)

    @exception_handler
    def save(self, data, path: str, **kwargs):
        np.savez(path, **data, **kwargs)


class NpyFileHandler(FileHandler):
    @exception_handler
    def load(self, path: str, **kwargs):
        return np.load(path, **kwargs)

    @exception_handler
    def save(self, data, path: str, **kwargs):
        np.save(path, data, **kwargs)


class Hdf5FileHandler(FileHandler):
    @exception_handler
    def load(self, path: str, **kwargs):
        return pd.read_hdf(path, **kwargs)

    @exception_handler
    def save(self, data, path: str, **kwargs):
        data.to_hdf(path, key="df", mode="w", **kwargs)


class FeatherFileHandler(FileHandler):
    @exception_handler
    def load(self, path: str, **kwargs):
        return pd.read_feather(path, **kwargs)

    @exception_handler
    def save(self, data, path: str, **kwargs):
        data.to_feather(path, **kwargs)


class YamlFileHandler(FileHandler):
    @exception_handler
    def load(self, path: str, **kwargs):
        with open(path, "r", **kwargs) as file:
            return yaml.safe_load(file)

    @exception_handler
    def save(self, data, path: str, **kwargs):
        with open(path, "w", **kwargs) as file:
            yaml.dump(data, file, **kwargs)


class MatFileHandler(FileHandler):
    @exception_handler
    def load(self, path: str, **kwargs):
        return scipy.io.loadmat(path, **kwargs)

    @exception_handler
    def save(self, data, path: str, **kwargs):
        scipy.io.savemat(path, data, **kwargs)


class SqliteFileHandler(FileHandler):
    @exception_handler
    def load(self, path: str, **kwargs):
        return sqlite3.connect(path)

    @exception_handler
    def save(self, data, path: str, table_name="table", **kwargs):
        conn = sqlite3.connect(path)
        data.to_sql(table_name, conn, if_exists="replace", **kwargs)


class ImageFileHandler(FileHandler):
    @exception_handler
    def load(self, path: str, **kwargs):
        return Image.open(path, **kwargs)

    @exception_handler
    def save(self, data, path: str, **kwargs):
        data.save(path, **kwargs)


class AudioFileHandler(FileHandler):
    @exception_handler
    def load(self, path: str, **kwargs):
        return librosa.load(path, **kwargs)

    @exception_handler
    def save(self, data, path: str, sr=22050, **kwargs):
        librosa.output.write_wav(path, data, sr, **kwargs)


class VideoFileHandler(FileHandler):
    @exception_handler
    def load(self, path: str, **kwargs):
        return cv2.VideoCapture(path, **kwargs)

    @exception_handler
    def save(self, data, path: str, fourcc, fps, frame_size, **kwargs):
        out = cv2.VideoWriter(path, fourcc, fps, frame_size, **kwargs)
        for frame in data:
            out.write(frame)
        out.release()


class XmlFileHandler(FileHandler):
    @exception_handler
    def load(self, path: str, **kwargs):
        tree = ET.parse(path, **kwargs)
        return tree.getroot()

    @exception_handler
    def save(self, data, path: str, **kwargs):
        tree = ET.ElementTree(data)
        tree.write(path, **kwargs)


class MarkDownFileHandler(FileHandler):
    @exception_handler
    def load(self, path: str, **kwargs):
        with open(path, "r", **kwargs) as file:
            return file.read()

    @exception_handler
    def save(self, data, path: str, **kwargs):
        with open(path, "w", **kwargs) as file:
            file.write(data)


class FileHandlerFactory:
    @staticmethod
    def create_handler(file_type: str) -> FileHandler:
        handlers = {
            "txt": TextFileHandler(),
            "json": JsonFileHandler(),
            "csv": CsvFileHandler(),
            "xlsx": ExcelFileHandler(),
            "parquet": ParquetFileHandler(),
            "pkl": PickleFileHandler(),
            "npz": NpzFileHandler(),
            "npy": NpyFileHandler(),
            "h5": Hdf5FileHandler(),
            "feather": FeatherFileHandler(),
            "yaml": YamlFileHandler(),
            "mat": MatFileHandler(),
            "db": SqliteFileHandler(),
            "sqlite": SqliteFileHandler(),
            "jpg": ImageFileHandler(),
            "png": ImageFileHandler(),
            "wav": AudioFileHandler(),
            "mp3": AudioFileHandler(),
            "mp4": VideoFileHandler(),
            "avi": VideoFileHandler(),
            "xml": XmlFileHandler(),
            "md": MarkDownFileHandler(),
        }
        return handlers.get(file_type.lower(), None)


class FileIO:
    @staticmethod
    def load(path: str, return_filename=False, **kwargs):
        file_name, file_type = os.path.splitext(path)
        file_type = file_type.lstrip(".").lower()
        handler = FileHandlerFactory.create_handler(file_type)
        if handler:
            data = handler.load(path, **kwargs)
            return (data, os.path.basename(file_name)) if return_filename else data
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    @staticmethod
    def save(data, path: str, **kwargs):
        file_type = os.path.splitext(path)[1].lstrip(".").lower()
        handler = FileHandlerFactory.create_handler(file_type)
        if handler:
            return handler.save(data, path, **kwargs)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")


# from typing import Callable

# load: Callable[..., None] = FileIO.load
# save: Callable[..., None] = FileIO.save


def load(path: str, return_filename=False, **kwargs):
    file_name, file_type = os.path.splitext(path)
    file_type = file_type.lstrip(".").lower()
    handler = FileHandlerFactory.create_handler(file_type)
    if handler:
        data = handler.load(path, **kwargs)
        return (data, os.path.basename(file_name)) if return_filename else data
    else:
        raise ValueError(f"Unsupported file type: {file_type}")


def save(data, path: str, **kwargs):
    file_type = os.path.splitext(path)[1].lstrip(".").lower()
    handler = FileHandlerFactory.create_handler(file_type)
    if handler:
        return handler.save(data, path, **kwargs)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
