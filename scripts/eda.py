"""
Exploratory Data Analysis (EDA) utilities for football pass data.

This module provides a class-based interface for common EDA tasks such as
missing value analysis, class imbalance checking, data type inspection, and duplicate removal.
"""

import pandas as pd

class PassDataEDA:
    """
    Class for performing EDA on football pass data.

    :param df: The pandas DataFrame to analyze.
    :type df: pd.DataFrame
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def missing_values(self) -> pd.Series:
        """
        Print and return missing value counts for each column.

        :return: Series with missing value counts.
        :rtype: pd.Series
        """
        print("=== Missing Values ===")
        missing = self.df.isnull().sum()
        if missing.sum() > 0:
            print(missing[missing > 0])
        else:
            print("No missing values.\n")
        return missing

    def class_distribution(self, target_col: str = "pass_outcome") -> pd.Series:
        """
        Print and return class distribution for the target column.

        :param target_col: Name of the target column.
        :type target_col: str
        :return: Series with class counts.
        :rtype: pd.Series
        """
        print("=== Class Distribution ===")
        if target_col in self.df.columns:
            counts = self.df[target_col].value_counts()
            print(counts)
            print("\nPercentage:")
            print(self.df[target_col].value_counts(normalize=True) * 100)
            return counts
        else:
            print(f"'{target_col}' column not found. Check the correct target column name.")
            return pd.Series(dtype=int)

    def data_types(self) -> pd.Series:
        """
        Print and return data types of all columns.

        :return: Series with data types.
        :rtype: pd.Series
        """
        print("\n=== Data Types ===")
        dtypes = self.df.dtypes
        print(dtypes)
        return dtypes

    def remove_duplicates(self) -> pd.DataFrame:
        """
        Print duplicate row count, remove duplicates, and return the cleaned DataFrame.

        :return: DataFrame without duplicate rows.
        :rtype: pd.DataFrame
        """
        print("\n=== Duplicate Rows ===")
        dup_count = self.df.duplicated().sum()
        print(f"Total duplicated rows: {dup_count}")
        if dup_count > 0:
            self.df = self.df.drop_duplicates()
            print("Duplicates removed.")
        else:
            print("No duplicates to remove.")
        return self.df

def main():
    df = pd.read_pickle("../.pickle/pass_data.pkl") 
    eda = PassDataEDA(df)
    eda.missing_values()
    eda.class_distribution()
    eda.data_types()
    df_clean = eda.remove_duplicates()

if __name__ == "__main__":
    main()