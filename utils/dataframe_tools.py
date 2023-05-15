# Author: BrenoAV
"""
Module to perform operations of dataframe manipulation
"""

import datetime
import logging
import os
import pathlib
from pathlib import Path

import pandas as pd


def create_pivot_table_load_energy(
    file_path_str: str, sep: str = ";", encoding: str = "utf-8"
) -> pd.DataFrame:
    """Read a csv file and create a pivot table

    Parameters
    ----------
    file_path_str: str
        file path of the csv file
    sep: str
        Separator used in the CSV file. Defaults to ";"
    encoding: str
        Encoding used in the CSV file. Defaults to "utf-8"

    Returns
    -------
    df_pivot: pd.DataFrame
        A pivot table based on the CSV file.

    """
    file_path = Path(file_path_str)
    if file_path.exists():
        df = pd.read_csv(file_path, sep=sep, encoding=encoding)
    else:
        return pd.DataFrame()
    try:
        df_pivot = df.pivot_table(
            values=["val_cargaenergiamwmed"],
            index=["din_instante"],
            columns=["id_subsistema", "nom_subsistema"],
        )
        return df_pivot
    except KeyError as e:
        logging.exception(
            f"Error: {e}. Please check if the input CSV file contains the expected columns"
        )
        raise


def replace_zero_negative(
    df: pd.DataFrame, positive_mean: bool = True, value: float = 99.0
) -> pd.DataFrame:
    """Function for replacing negative/zero values for the mean of the positive values on
    the column, or for other value if positive_mean is equal to False

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to be modified
    positive_mean : bool, optional (default: True)
        If True, replaces zero or negative values with the mean of positive values in each column
        If False, replaces zero or negative values with the specified value
    value : float, optional (default: 99.0)
        The value to replace zero or negative values if positive_mean is False

    Returns
    -------
    pd.DataFrame
        A copy of the original DataFrame with zero or negative values replaced according to the
        specified parameters
    """
    df_copy = df.copy()
    zero_negative_mask = df_copy <= 0.0
    logging.info(
        f"Number of negative values in dataframe = {(df_copy < 0).all().sum()}"
    )
    logging.info(f"Number of zero values in dataframe = {(df_copy == 0).all().sum()}")
    if positive_mean:
        for col in df_copy.columns:
            positive_mask = df_copy > 0
            positive_values = df_copy.loc[positive_mask[col], col]
            positive_mean = positive_values.mean()
            df_copy.loc[zero_negative_mask[col], col] = positive_mean

    else:
        df_copy[zero_negative_mask] = value

    return df_copy


def data_clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean dataframe with the following possible problems:
        - NAs values
        - Zero values
        - Negative values

    Parameters
    ----------
        df: pd.DataFrame
            DataFrame to be cleared

    Returns
    -------
        df: pd.DataFrame
            Cleared DataFrame
    """
    df_copy = df.copy()
    count_nas = df_copy.isna().sum().sum()
    logging.info(f"Number of NAs values = {count_nas}")
    if count_nas > 0:
        logging.info("Replacing NAs values with the next value...")
        df_copy.fillna(method="bfill", inplace=True)
    df_copy = replace_zero_negative(df_copy)
    logging.info("DataFrame cleaned!")
    return df_copy


def save_csv(
    df: pd.DataFrame, path_to_save: pathlib.Path, filename: str, index: bool = True
) -> None:
    """Save dataframe in a csv file

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe to be saved
    path_to_save : pathlib.Path
        A directory for saving the file, if doesn't exist will be created
    filename : str
        csv filename
    index : bool
        If is False will not save the index, by default True
    """
    path_to_save.mkdir(exist_ok=True, parents=True)
    df.to_csv(
        os.path.join(path_to_save, filename + ".csv"),
        sep=",",
        encoding="utf-8",
        index=index,
    )
    logging.info(f"Dataframe {os.path.join(path_to_save, f'{filename}.csv')} saved!")


def check_date_range_energy_load(
    df_series: pd.DatetimeIndex, start_year: int, end_year: int
) -> bool:
    """Compare the series of date range to check if the interval is correct

    Parameters
    ----------
    df_series : pd.DatetimeIndex
        Series to be compared with the range of years specified
    start_year : int
        The year to start the range (monthly)
    end_year : int
        The year to end the range (monthly)

    Returns
    -------
    bool
        True if the df_series has the correct date range

    Raises
    ------
    TypeError
        if df_series is not a Pandas DatetimeIndex
    TypeError
        if start_year is not an integer
    TypeError
        if end_year is not an integer
    ValueError
        if start_year is greater than end_year
    ValueError
        if date range comparasion fails
    """
    if not isinstance(df_series, pd.DatetimeIndex):
        raise TypeError("df must be a pandas DatetimeIndex")
    if not isinstance(start_year, int):
        raise TypeError("start_year must be an integer")
    if not isinstance(end_year, int):
        raise TypeError("end_year must be an integer")

    if end_year < start_year:
        raise ValueError(
            "start_year must be an integer equal to or lower than end_year"
        )

    start_date = datetime.date(start_year, 1, 1)
    end_date = datetime.date(end_year, 12, 31)
    date_range = pd.date_range(start=start_date, end=end_date)
    try:
        return (df_series == date_range).any()
    except ValueError as e:
        raise ValueError("Failed to compare date rangers.") from e
