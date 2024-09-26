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


def exception_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"An error occurred in {func.__name__}: {str(e)}")
            return None

    return wrapper


class FileHandler:
    load_handlers = {
        "txt": "_load_txt",
        "json": "_load_json",
        "csv": "_load_csv",
        "xlsx": "_load_excel",
        "parquet": "_load_parquet",
        "pkl": "_load_pickle",
        "npz": "_load_npz",
        "npy": "_load_npy",
        "h5": "_load_hdf5",
        "feather": "_load_feather",
        "yaml": "_load_yaml",
        "mat": "_load_mat",
        "db": "_load_sqlite",
        "sqlite": "_load_sqlite",
        "jpg": "_load_image",
        "png": "_load_image",
        "wav": "_load_audio",
        "mp3": "_load_audio",
        "mp4": "_load_video",
        "avi": "_load_video",
        "xml": "_load_xml",
    }

    save_handlers = {
        "txt": "_save_txt",
        "json": "_save_json",
        "csv": "_save_csv",
        "xlsx": "_save_excel",
        "parquet": "_save_parquet",
        "pkl": "_save_pickle",
        "npz": "_save_npz",
        "npy": "_save_npy",
        "h5": "_save_hdf5",
        "feather": "_save_feather",
        "yaml": "_save_yaml",
        "mat": "_save_mat",
        "db": "_save_sqlite",
        "sqlite": "_save_sqlite",
        "jpg": "_save_image",
        "png": "_save_image",
        "wav": "_save_audio",
        "mp3": "_save_audio",
        "mp4": "_save_video",
        "avi": "_save_video",
        "xml": "_save_xml",
    }

    @staticmethod
    def load(path: str, fn=False, **kwargs):
        try:
            file_name, file_type = os.path.basename(path).split(".")
            file_type = file_type.lower()

            if file_type in FileHandler.load_handlers:
                handler_method = getattr(
                    FileHandler, FileHandler.load_handlers[file_type]
                )
                if not fn:
                    return handler_method(path, **kwargs)
                else:
                    return handler_method(path, **kwargs), file_name
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    @staticmethod
    def save(data, path: str, **kwargs):
        try:
            file_type = os.path.basename(path).split(".")[-1].lower()

            if file_type in FileHandler.save_handlers:
                handler_method = getattr(
                    FileHandler, FileHandler.save_handlers[file_type]
                )
                return handler_method(data, path, **kwargs)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    @exception_handler
    def _load_txt(path, **kwargs):
        with open(path, "r", **kwargs) as file:
            return file.read()

    @exception_handler
    def _save_txt(data, path, **kwargs):
        with open(path, "w", **kwargs) as file:
            file.write(data)

    @exception_handler
    def _load_json(path):
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    @exception_handler
    def _save_json(data, path, **kwargs):
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, **kwargs)

    @exception_handler
    def _load_csv(path, **kwargs):
        return pd.read_csv(path, **kwargs)

    @exception_handler
    def _save_csv(data, path, **kwargs):
        data.to_csv(path, **kwargs)

    @exception_handler
    def _load_excel(path, **kwargs):
        return pd.read_excel(path, **kwargs)

    @exception_handler
    def _save_excel(data, path, **kwargs):
        data.to_excel(path, **kwargs)

    @exception_handler
    def _load_parquet(path, **kwargs):
        return pd.read_parquet(path, **kwargs)

    @exception_handler
    def _save_parquet(data, path, **kwargs):
        data.to_parquet(path, **kwargs)

    @exception_handler
    def _load_pickle(path, **kwargs):
        with open(path, "rb", **kwargs) as file:
            return pickle.load(file)

    @exception_handler
    def _save_pickle(data, path, **kwargs):
        with open(path, "wb", **kwargs) as file:
            pickle.dump(data, file, **kwargs)

    @exception_handler
    def _load_npz(path, **kwargs):
        return np.load(path, **kwargs)

    @exception_handler
    def _save_npz(data, path, **kwargs):
        np.savez(path, **data, **kwargs)

    @exception_handler
    def _load_npy(path, **kwargs):
        return np.load(path, **kwargs)

    @exception_handler
    def _save_npy(data, path, **kwargs):
        np.save(path, data, **kwargs)

    @exception_handler
    def _load_hdf5(path, **kwargs):
        return pd.read_hdf(path, **kwargs)

    @exception_handler
    def _save_hdf5(data, path, **kwargs):
        data.to_hdf(path, key="df", mode="w", **kwargs)

    @exception_handler
    def _load_feather(path, **kwargs):
        return pd.read_feather(path, **kwargs)

    @exception_handler
    def _save_feather(data, path, **kwargs):
        data.to_feather(path, **kwargs)

    @exception_handler
    def _load_yaml(path, **kwargs):
        with open(path, "r", **kwargs) as file:
            return yaml.safe_load(file)

    @exception_handler
    def _save_yaml(data, path, **kwargs):
        with open(path, "w", **kwargs) as file:
            yaml.dump(data, file, **kwargs)

    @exception_handler
    def _load_mat(path, **kwargs):
        return scipy.io.loadmat(path, **kwargs)

    @exception_handler
    def _save_mat(data, path, **kwargs):
        scipy.io.savemat(path, data, **kwargs)

    @exception_handler
    def _load_sqlite(path, **kwargs):
        conn = sqlite3.connect(path)
        return conn

    @exception_handler
    def _save_sqlite(data, path, table_name="table", **kwargs):
        conn = sqlite3.connect(path)
        data.to_sql(table_name, conn, if_exists="replace", **kwargs)

    @exception_handler
    def _load_image(path, **kwargs):
        return Image.open(path, **kwargs)

    @exception_handler
    def _save_image(data, path, **kwargs):
        data.save(path, **kwargs)

    @exception_handler
    def _load_audio(path, **kwargs):
        return librosa.load(path, **kwargs)

    @exception_handler
    def _save_audio(data, path, sr=22050, **kwargs):
        librosa.output.write_wav(path, data, sr, **kwargs)

    @exception_handler
    def _load_video(path, **kwargs):
        return cv2.VideoCapture(path, **kwargs)

    @exception_handler
    def _save_video(data, path, fourcc, fps, frame_size, **kwargs):
        out = cv2.VideoWriter(path, fourcc, fps, frame_size, **kwargs)
        for frame in data:
            out.write(frame)
        out.release()

    @exception_handler
    def _load_xml(path, **kwargs):
        tree = ET.parse(path, **kwargs)
        return tree.getroot()

    @exception_handler
    def _save_xml(data, path, **kwargs):
        tree = ET.ElementTree(data)
        tree.write(path, **kwargs)

