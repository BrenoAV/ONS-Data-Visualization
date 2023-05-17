# Author: BrenoAV
"""
Module to perform operations of dataframe manipulation
"""

import datetime
import logging
import os
import pathlib

import numpy as np
import pandas as pd


def create_pivot_table_load_energy(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Create a load energy pivot table

    Parameters
    ----------
    df_raw : pd.DataFrame
        A raw DataFrame with the columns: "val_cargaenergiamwmed",
                                          "din_instante",
                                          "id_subsistema",
                                          "nom_subsistema"

    Returns
    -------
    df_pivot: pd.DataFrame
        A pivot table based on the CSV file

    """
    try:
        df_pivot = df_raw.pivot_table(
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
    df_datetime_index: pd.DatetimeIndex,
    start_date: datetime.date,
    end_date: datetime.date,
) -> bool:
    """Check if the range of the date between the min and max date are correctly

    Parameters
    ----------
    df_datetime_index : pd.DatetimeIndex
        Series DateTimeIndex to be evaluated if the values are correctly (date range)
    start_date : datetime.date
        start date to create a range of date
    end_date : datetime.date
        end date to create a range of date

    Returns
    -------
    bool
        True if the values are correct or False, otherwise

    Raises
    ------
    TypeError
        Check if df_date_time_index is a DatetimeIndex valid
    TypeError
        Check if start_date is a valid datetime.date
    TypeError
        Check if end_date is a valid datetime.date
    ValueError
        raise if the end_date is before the start_date
    ValueError
        raise if the datetime has no same size that the specified range
    """
    if not isinstance(df_datetime_index, pd.DatetimeIndex):
        raise TypeError("df_datetime_index must be a pandas DatetimeIndex")
    if not isinstance(start_date, datetime.date):
        raise TypeError("start_date must be an datetime.date")
    if not isinstance(end_date, datetime.date):
        raise TypeError("end_date must be an datetime.date")

    if end_date < start_date:
        raise ValueError(
            "start_date must be an integer equal to or lower than end_date"
        )

    date_range = pd.date_range(start=start_date, end=end_date)
    try:
        return np.all((df_datetime_index == date_range) == True)
    except ValueError as e:
        raise ValueError(
            f"Failed to compare date ranges. {len(df_datetime_index)} != {len(date_range)} "
        ) from e
