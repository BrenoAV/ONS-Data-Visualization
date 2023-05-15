# Author: BrenoAV
# -*- coding: utf-8 -*-

import os
import unittest
from pathlib import Path
from shutil import rmtree

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from utils.dataframe_tools import (
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
        self.filepath = Path("tmp")
        self.filename = "tmp"
        self.df = pd.DataFrame({"col1": [1, 2], "B": ["foo", "bar"]})

    def test_save_csv_file_creation(self):
        # creating a mock csv
        save_csv(self.df, self.filepath, self.filename)
        # Assert that the file was created
        self.assertTrue(os.path.isfile(os.path.join(self.filepath, self.filename)))

        df_loaded = pd.read_csv(
            os.path.join(self.filepath, self.filename), sep=",", encoding="utf-8"
        )

        # Assert that the content of the file is equals to original
        self.assertTrue(self.df.equals(df_loaded))

        # Deleting tmp files (mock files)
        if self.filepath is not os.getcwd():
            rmtree(self.filepath)
        else:
            if os.path.exists(self.filename):
                os.remove(self.filename)


class TestCreatePivotTableLoadEnergy(unittest.TestCase):
    """Test Class"""

    def setUp(self):
        self.tmp_dir = Path("tmp")
        self.tmp_dir.mkdir(exist_ok=True)

    def _create_valid_sample_csv(self, file_path):
        data = {
            "id_subsistema": ["N", "NE"],
            "nom_subsistema": ["Norte", "Nordeste"],
            "din_instante": ["2030-01-04", "2030-01-04"],
            "val_cargaenergiamwmed": [450000, 500000],
        }
        df = pd.DataFrame(data)
        df.to_csv(file_path, sep=";", index=False, encoding="utf-8")

    def _create_invalid_sample_csv(self, file_path):
        data = {
            "iD_subsistema": ["N", "NE"],
            "A": ["Norte", "Nordeste"],
            "din_instante": ["2030-01-04", "2030-01-04"],
            "val_cargaenergiamwmed": [450000, 500000],
        }
        df = pd.DataFrame(data)
        df.to_csv(file_path, sep=";", index=False, encoding="utf-8")

    def test_create_pivot_table_load_energy_with_valid_csv(self):
        file_path = os.path.join(self.tmp_dir, "valid.csv")
        self._create_valid_sample_csv(file_path)
        expected_output = pd.DataFrame(
            data={
                ("val_cargaenergiamwmed", "N", "Norte"): 450000,
                ("val_cargaenergiamwmed", "NE", "Nordeste"): 500000,
            },
            index=pd.Index(data=["2030-01-04"], dtype="object", name="din_instante"),
            columns=pd.MultiIndex.from_tuples(
                [
                    ("val_cargaenergiamwmed", "N", "Norte"),
                    ("val_cargaenergiamwmed", "NE", "Nordeste"),
                ],
                names=[None, "id_subsistema", "nom_subsistema"],
            ),
        )
        df_out = create_pivot_table_load_energy(file_path)
        # Assert that the two dataframes are equals after the function
        assert_frame_equal(df_out, expected_output)

    def test_create_pivot_table_load_energy_with_non_exists_csv(self):
        file_path = os.path.join(self.tmp_dir, "non_exists.csv")
        df_output = create_pivot_table_load_energy(file_path)
        # Assert a empty dataframe when the file path dosn't exist
        self.assertTrue(df_output.empty)

    def test_create_pivot_table_load_energy_invalid_columns(self):
        file_path = os.path.join(self.tmp_dir, "invalid_columns.csv")
        self._create_invalid_sample_csv(file_path)
        # Assert that with a invalid column returns a KeyError exception
        self.assertRaises(KeyError, create_pivot_table_load_energy, file_path)

    def tearDown(self):
        rmtree(self.tmp_dir)


if __name__ == "__main__":
    unittest.main()
