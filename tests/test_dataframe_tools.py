# Author: BrenoAV
# -*- coding: utf-8 -*-
""" utils -> dataframe_tools tests """

import datetime
import os
import unittest
from pathlib import Path
from shutil import rmtree

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from utils.dataframe_tools import (
    check_date_range_energy_load,
    create_pivot_table_load_energy,
    data_clean,
    replace_zero_negative,
    save_csv,
)


class TestDataClean(unittest.TestCase):
    """Test Class"""

    def setUp(self):
        self.df = pd.DataFrame({"A": [1, 2, np.nan, 4], "B": [np.nan, 6, 7, 8]})

    def test_data_clean(self):
        # Test the function with a DataFrame that has missing values
        df_cleaned = data_clean(self.df)
        # assert that there are no missing values
        self.assertEqual(df_cleaned.isna().sum().sum(), 0)
        # assert that the shape is the same
        self.assertEqual(self.df.shape, df_cleaned.shape)
        # assert backpropagation value if the value is NaN
        self.assertEqual(df_cleaned["A"].iloc[2], 4)
        # assert backpropagation value if the value is NaN
        self.assertEqual(df_cleaned["B"].iloc[0], 6)

        # Test the function with a DataFrame that has no missing values
        df_no_missing = data_clean(df_cleaned)
        # assert that the input and output is the same
        self.assertTrue(df_no_missing.equals(df_cleaned))


class TestZeroNegative(unittest.TestCase):
    """Test Class"""

    def setUp(self):
        self.df = pd.DataFrame({"A": [1, -2, 0, 3], "B": [0, 6, 7, -8]})

    def test_replace_zero_negative(self):
        # Test the function with a DataFrame that has negative and zero values
        df_replaced = replace_zero_negative(self.df)

        # assert there're no negative values
        self.assertEqual((df_replaced < 0).any().sum(), 0)
        # assert there're no zero values
        self.assertEqual((df_replaced == 0).any().sum(), 0)
        # assert the input and ouput shape are the same
        self.assertEqual(self.df.shape, df_replaced.shape)

        # Test with a dataframe that has no zero or negative values
        df_no_neg_no_zero = replace_zero_negative(df_replaced)
        # assert there're no changes and that the dataframe is the same
        self.assertTrue(df_no_neg_no_zero.equals(df_replaced))

    def test_replace_zero_negative_with_mean_pos(self):
        # Test the function with a DataFrame that has negative and zero values
        df_replaced = replace_zero_negative(self.df, positive_mean=True, value=100)

        # assert that the values were replaced with the mean of positive values
        self.assertEqual(df_replaced.iat[1, 0], 2)
        self.assertEqual(df_replaced.iat[2, 0], 2)
        self.assertEqual(df_replaced.iat[0, 1], 6.5)
        self.assertEqual(df_replaced.iat[3, 1], 6.5)

    def test_replace_zero_negative_with_specified_value(self):
        # Test the function with a DataFrame that has negative and zero values
        df_replaced = replace_zero_negative(self.df, positive_mean=False, value=100)

        # assert that the values were replaced with the value specified
        self.assertEqual(df_replaced.iat[1, 0], 100)
        self.assertEqual(df_replaced.iat[2, 0], 100)
        self.assertEqual(df_replaced.iat[0, 1], 100)
        self.assertEqual(df_replaced.iat[3, 1], 100)

        # assert that the shape is the same
        self.assertEqual(df_replaced.shape, self.df.shape)


class TestFileOperations(unittest.TestCase):
    """Test Class"""

    def setUp(self):
        self.tmp_dir = Path("tmp")
        self.filename = "filename"
        self.df = pd.DataFrame({"col1": [1, 2], "B": ["foo", "bar"]})

    def test_save_csv_file_creation(self):
        # creating a mock csv
        save_csv(self.df, self.tmp_dir, self.filename, index=False)
        # Assert that the file was created
        self.assertTrue(
            os.path.isfile(os.path.join(self.tmp_dir, self.filename + ".csv"))
        )

        df_loaded = pd.read_csv(
            os.path.join(self.tmp_dir, self.filename + ".csv"),
            sep=",",
            encoding="utf-8",
        )

        # Assert that the content of the file is equals to original
        self.assertTrue(self.df.equals(df_loaded))

    def tearDown(self):
        rmtree(self.tmp_dir)


class TestCreatePivotTableLoadEnergy(unittest.TestCase):
    """Test Class"""

    def setUp(self):
        self.tmp_dir = Path("tmp")
        self.tmp_dir.mkdir(exist_ok=True)
        self.df_valid = pd.DataFrame(
            data={
                "id_subsistema": ["N", "NE", "S", "SE"],
                "nom_subsistema": ["Norte", "Nordeste", "Sul", "Sudeste/Centro-Oeste"],
                "din_instante": [
                    "2030-01-01",
                    "2030-01-01",
                    "2030-01-01",
                    "2030-01-01",
                ],
                "val_cargaenergiamwmed": [50000, 60000, 70000, 100000],
            }
        )
        self.df_invalid = pd.DataFrame(
            data={
                "ida_subsistema": ["N", "NE", "S", "SE"],
                "nom_subsistema": ["Norte", "Nordeste", "sul", "Sudeste/Centro-Oeste"],
                "din_instante": [
                    "2030-01-01",
                    "2030-01-01",
                    "2030-01-01",
                    "2030-01-01",
                ],
                "val_cargaenergiamwmed": [50000, 60000, 70000, 100000],
            }
        )

    def test_create_pivot_table_load_energy_valid(self):
        df_output = create_pivot_table_load_energy(self.df_valid)
        tuples_expected = [
            ("val_cargaenergiamwmed", "N", "Norte"),
            ("val_cargaenergiamwmed", "NE", "Nordeste"),
            ("val_cargaenergiamwmed", "S", "Sul"),
            ("val_cargaenergiamwmed", "SE", "Sudeste/Centro-Oeste"),
        ]
        columns_expected = pd.MultiIndex.from_tuples(
            tuples_expected, names=[None, "id_subsistema", "nom_subsistema"]
        )
        data_expected = [[50000, 60000, 70000, 100000]]
        df_expected = pd.DataFrame(
            data_expected, columns=columns_expected, index=["2030-01-01"]
        )
        df_expected.index.name = "din_instante"

        assert_frame_equal(df_output, df_expected)

    def test_create_pivot_table_load_energy_invalid_columns(self):
        self.assertRaises(KeyError, create_pivot_table_load_energy, self.df_invalid)

    def tearDown(self):
        rmtree(self.tmp_dir)


class TestCheckDateRangeEnergyLoad(unittest.TestCase):
    def setUp(self):
        self.start_date = datetime.date(2030, 1, 1)
        self.end_date = datetime.date(2030, 1, 7)
        self.date_range_valid = pd.DatetimeIndex(
            [
                "2030-01-01",
                "2030-01-02",
                "2030-01-03",
                "2030-01-04",
                "2030-01-05",
                "2030-01-06",
                "2030-01-07",
            ]
        )
        self.date_range_invalid = pd.DatetimeIndex(
            [
                "2030-01-01",
                "2030-01-03",
                "2030-01-04",
                "2030-01-05",
                "2030-01-06",
                "2030-01-07",
                "2030-01-07",
            ]
        )

    def test_check_date_range_energy_load_valid_date(self):
        self.assertTrue(
            check_date_range_energy_load(
                self.date_range_valid, self.start_date, self.end_date
            )
        )

    def test_check_date_range_energy_load_invalid_date(self):
        self.assertFalse(
            check_date_range_energy_load(
                self.date_range_invalid, self.start_date, self.end_date
            )
        )

    def test_check_date_range_energy_load_invalid_size(self):
        # assert that if the date range is less than expected range using the start_date
        # and end_date raises a error
        self.assertRaises(
            ValueError,
            check_date_range_energy_load,
            self.date_range_invalid[:-2],
            self.start_date,
            self.end_date,
        )


if __name__ == "__main__":
    unittest.main()
