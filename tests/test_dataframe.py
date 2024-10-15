import pytest
import pandas as pd
import numpy as np
import os
from ..dh_tool.dataframe.core.sheets import Sheets


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "A": [1, 2, 3, 4, 5],
            "B": ["a", "b", "c", "d", "e"],
            "C": [1.1, 2.2, 3.3, 4.4, 5.5],
        }
    )


def test_create_sheets(sample_df):
    sheets = Sheets(sample_df)
    assert sheets.df.equals(sample_df)


def test_excel_operations(sample_df, tmp_path):
    sheets = Sheets(sample_df)

    # Test creating a new sheet
    sheets.create_sheet(sample_df, "Sheet2")
    assert "Sheet2" in sheets.sheet_names

    # Test selecting a sheet
    sheets.select_sheet("Sheet2")
    assert sheets.current_sheet == "Sheet2"

    # Test saving and loading Excel file
    file_path = tmp_path / "test.xlsx"
    sheets.save(str(file_path))
    assert os.path.exists(file_path)

    # Test removing a sheet
    sheets.remove_sheet("Sheet2")
    assert "Sheet2" not in sheets.sheet_names


def test_dataframe_operations(sample_df):
    sheets = Sheets(sample_df)

    # Test filtering rows
    filtered = sheets.select_rows(include={"A": 1})
    assert len(filtered) == 1
    assert filtered.iloc[0]["A"] == 1

    # Test group and aggregate
    grouped = sheets.group_and_aggregate("B", mean="mean")
    assert len(grouped) == 5
    assert "mean" in grouped.columns

    # Test fill missing
    sheets.df.loc[0, "A"] = np.nan
    filled = sheets.fill_missing(strategy="mean", columns=["A"])
    assert not filled["A"].isnull().any()

    # Test normalize
    normalized = sheets.normalize(columns=["C"])
    assert normalized["C"].min() == 0
    assert normalized["C"].max() == 1


def test_visualization(sample_df, tmp_path):
    sheets = Sheets(sample_df)

    # Test histogram plot
    sheets.plot_histogram("A")

    # Test scatter plot
    sheets.plot_scatter("A", "C")

    # Test saving plot
    file_path = tmp_path / "test_plot.png"
    sheets.visualization_handler.save_plot(str(file_path))
    assert os.path.exists(file_path)


def test_excel_styling(sample_df, tmp_path):
    sheets = Sheets(sample_df)

    # Test setting column width
    sheets.set_column_width(A=20, B=15)

    # Test freezing first row
    sheets.freeze_first_row()

    # Test enabling auto wrap
    sheets.enable_autowrap()

    # Test adding hyperlink
    sheets.add_hyperlink("A1", "https://example.com", "Example")

    # Save and check if file is created
    file_path = tmp_path / "styled.xlsx"
    sheets.save(str(file_path))
    assert os.path.exists(file_path)


def test_event_emitting(sample_df):
    sheets = Sheets(sample_df)

    # Test if handlers are updated when sheet is changed
    new_df = pd.DataFrame({"X": [1, 2, 3], "Y": [4, 5, 6]})
    sheets.create_sheet(new_df, "NewSheet")
    sheets.select_sheet("NewSheet")

    assert sheets.df.equals(new_df)
    assert sheets.df_handler.df.equals(new_df)
    assert sheets.visualization_handler.df.equals(new_df)
    assert sheets.excel_handler.df.equals(new_df)
