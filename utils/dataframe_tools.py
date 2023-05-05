# !/usr/bin/env python
# Author: BrenoAV
"""
Module to perform operations of dataframe manipulation
"""

import pandas as pd
import numpy as np
import logging

"""
TODO: Create a function for transform the raw data from ONS Dados Abertos into a valid format
"""


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
