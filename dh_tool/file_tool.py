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
    def __init__(self):
        self.load_handlers = {
            "txt": self._load_txt,
            "json": self._load_json,
            "csv": self._load_csv,
            "xlsx": self._load_excel,
            "parquet": self._load_parquet,
            "pkl": self._load_pickle,
            "npz": self._load_npz,
            "npy": self._load_npy,
            "h5": self._load_hdf5,
            "feather": self._load_feather,
            "yaml": self._load_yaml,
            "mat": self._load_mat,
            "db": self._load_sqlite,
            "sqlite": self._load_sqlite,
            "jpg": self._load_image,
            "png": self._load_image,
            "wav": self._load_audio,
            "mp3": self._load_audio,
            "mp4": self._load_video,
            "avi": self._load_video,
            "xml": self._load_xml,
        }
        self.save_handlers = {
            "txt": self._save_txt,
            "json": self._save_json,
            "csv": self._save_csv,
            "xlsx": self._save_excel,
            "parquet": self._save_parquet,
            "pkl": self._save_pickle,
            "npz": self._save_npz,
            "npy": self._save_npy,
            "h5": self._save_hdf5,
            "feather": self._save_feather,
            "yaml": self._save_yaml,
            "mat": self._save_mat,
            "db": self._save_sqlite,
            "sqlite": self._save_sqlite,
            "jpg": self._save_image,
            "png": self._save_image,
            "wav": self._save_audio,
            "mp3": self._save_audio,
            "mp4": self._save_video,
            "avi": self._save_video,
            "xml": self._save_xml,
        }

    def load(self, path: str, fn=False, **kwargs):
        try:
            file_name, file_type = os.path.basename(path).split(".")
            file_type = file_type.lower()

            if file_type in self.load_handlers:
                if not fn:
                    return self.load_handlers[file_type](path, **kwargs)
                else:
                    return self.load_handlers[file_type](path, **kwargs), file_name
            else:
                raise ValueError(f"Unsupported file type: {file_type}")

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def save(self, data, path: str, **kwargs):
        try:
            file_type = os.path.basename(path).split(".")[-1].lower()

            if file_type in self.save_handlers:
                return self.save_handlers[file_type](data, path, **kwargs)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    @exception_handler
    def _load_txt(self, path, **kwargs):
        with open(path, "r", **kwargs) as file:
            return file.read()

    @exception_handler
    def _save_txt(self, data, path, **kwargs):
        with open(path, "w", **kwargs) as file:
            file.write(data)

    @exception_handler
    def _load_json(self, path, **kwargs):
        with open(path, "r", **kwargs) as file:
            return json.load(file)

    @exception_handler
    def _save_json(self, data, path, **kwargs):
        with open(path, "w", **kwargs) as file:
            json.dump(data, file, **kwargs)

    @exception_handler
    def _load_csv(self, path, **kwargs):
        return pd.read_csv(path, **kwargs)

    @exception_handler
    def _save_csv(self, data, path, **kwargs):
        data.to_csv(path, **kwargs)

    @exception_handler
    def _load_excel(self, path, **kwargs):
        return pd.read_excel(path, **kwargs)

    @exception_handler
    def _save_excel(self, data, path, **kwargs):
        data.to_excel(path, **kwargs)

    @exception_handler
    def _load_parquet(self, path, **kwargs):
        return pd.read_parquet(path, **kwargs)

    @exception_handler
    def _save_parquet(self, data, path, **kwargs):
        data.to_parquet(path, **kwargs)

    @exception_handler
    def _load_pickle(self, path, **kwargs):
        with open(path, "rb", **kwargs) as file:
            return pickle.load(file)

    @exception_handler
    def _save_pickle(self, data, path, **kwargs):
        with open(path, "wb", **kwargs) as file:
            pickle.dump(data, file, **kwargs)

    @exception_handler
    def _load_npz(self, path, **kwargs):
        return np.load(path, **kwargs)

    @exception_handler
    def _save_npz(self, data, path, **kwargs):
        np.savez(path, **data, **kwargs)

    @exception_handler
    def _load_npy(self, path, **kwargs):
        return np.load(path, **kwargs)

    @exception_handler
    def _save_npy(self, data, path, **kwargs):
        np.save(path, data, **kwargs)

    @exception_handler
    def _load_hdf5(self, path, **kwargs):
        return pd.read_hdf(path, **kwargs)

    @exception_handler
    def _save_hdf5(self, data, path, **kwargs):
        data.to_hdf(path, key="df", mode="w", **kwargs)

    @exception_handler
    def _load_feather(self, path, **kwargs):
        return pd.read_feather(path, **kwargs)

    @exception_handler
    def _save_feather(self, data, path, **kwargs):
        data.to_feather(path, **kwargs)

    @exception_handler
    def _load_yaml(self, path, **kwargs):
        with open(path, "r", **kwargs) as file:
            return yaml.safe_load(file)

    @exception_handler
    def _save_yaml(self, data, path, **kwargs):
        with open(path, "w", **kwargs) as file:
            yaml.dump(data, file, **kwargs)

    @exception_handler
    def _load_mat(self, path, **kwargs):
        return scipy.io.loadmat(path, **kwargs)

    @exception_handler
    def _save_mat(self, data, path, **kwargs):
        scipy.io.savemat(path, data, **kwargs)

    @exception_handler
    def _load_sqlite(self, path, **kwargs):
        conn = sqlite3.connect(path)
        return conn

    @exception_handler
    def _save_sqlite(self, data, path, table_name="table", **kwargs):
        conn = sqlite3.connect(path)
        data.to_sql(table_name, conn, if_exists="replace", **kwargs)

    @exception_handler
    def _load_image(self, path, **kwargs):
        return Image.open(path, **kwargs)

    @exception_handler
    def _save_image(self, data, path, **kwargs):
        data.save(path, **kwargs)

    @exception_handler
    def _load_audio(self, path, **kwargs):
        return librosa.load(path, **kwargs)

    @exception_handler
    def _save_audio(self, data, path, sr=22050, **kwargs):
        librosa.output.write_wav(path, data, sr, **kwargs)

    @exception_handler
    def _load_video(self, path, **kwargs):
        return cv2.VideoCapture(path, **kwargs)

    @exception_handler
    def _save_video(self, data, path, fourcc, fps, frame_size, **kwargs):
        out = cv2.VideoWriter(path, fourcc, fps, frame_size, **kwargs)
        for frame in data:
            out.write(frame)
        out.release()

    @exception_handler
    def _load_xml(self, path, **kwargs):
        tree = ET.parse(path, **kwargs)
        return tree.getroot()

    @exception_handler
    def _save_xml(self, data, path, **kwargs):
        tree = ET.ElementTree(data)
        tree.write(path, **kwargs)
