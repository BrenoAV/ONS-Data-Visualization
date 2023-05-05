import unittest
import pandas as pd
import numpy as np
from utils.dataframe_tools import data_clean, replace_zero_negative


class TestDataClean(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
