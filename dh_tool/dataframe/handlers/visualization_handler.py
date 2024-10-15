import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

from ..utils.events import EventEmitter


class VisualizationHandler(EventEmitter):
    def __init__(self):
        super().__init__()
        self.df = None

    def update(self, dataframe):
        self.df = dataframe
        self.emit("data_updated", self.df)

    def plot_histogram(self, column, bins=10, title=None):
        plt.figure(figsize=(10, 6))
        sns.histplot(self.df[column], bins=bins)
        plt.title(title if title else f"Histogram of {column}")
        plt.xlabel(column)
        plt.ylabel("Frequency")
        plt.show()

    def plot_boxplot(self, column, by=None, title=None):
        plt.figure(figsize=(10, 6))
        sns.boxplot(x=by, y=column, data=self.df)
        plt.title(title if title else f"Boxplot of {column}")
        plt.xlabel(by if by else "Category")
        plt.ylabel(column)
        plt.show()

    def plot_scatter(self, x, y, hue=None, title=None):
        plt.figure(figsize=(10, 6))
        sns.scatterplot(x=x, y=y, hue=hue, data=self.df)
        plt.title(title if title else f"Scatter Plot of {x} vs {y}")
        plt.xlabel(x)
        plt.ylabel(y)
        plt.show()

    def plot_heatmap(self, title=None):
        plt.figure(figsize=(12, 8))
        sns.heatmap(self.df.corr(), annot=True, fmt=".2f", cmap="coolwarm")
        plt.title(title if title else "Correlation Heatmap")
        plt.show()

    def plot_bar(self, x, y, hue=None, title=None):
        plt.figure(figsize=(10, 6))
        sns.barplot(x=x, y=y, hue=hue, data=self.df)
        plt.title(title if title else f"Bar Plot of {x} vs {y}")
        plt.xlabel(x)
        plt.ylabel(y)
        plt.show()

    def plot_line(self, x, y, hue=None, title=None):
        plt.figure(figsize=(10, 6))
        sns.lineplot(x=x, y=y, hue=hue, data=self.df)
        plt.title(title if title else f"Line Plot of {x} vs {y}")
        plt.xlabel(x)
        plt.ylabel(y)
        plt.show()

    def quick_plot(self, kind, x=None, y=None, **kwargs):
        """빠른 플롯 생성"""
        self.df.plot(kind=kind, x=x, y=y, **kwargs)
        plt.show()

    def pairplot(self, vars=None, hue=None, **kwargs):
        """페어플롯 생성"""
        sns.pairplot(self.df, vars=vars, hue=hue, **kwargs)
        plt.show()

    def violinplot(self, x=None, y=None, hue=None, **kwargs):
        """바이올린 플롯 생성"""
        plt.figure(figsize=(10, 6))
        sns.violinplot(x=x, y=y, hue=hue, data=self.df, **kwargs)
        plt.show()

    def save_plot(self, filename, dpi=300):
        """현재 플롯을 파일로 저장"""
        plt.savefig(filename, dpi=dpi)
