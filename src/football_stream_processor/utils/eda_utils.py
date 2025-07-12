# src/football_stream_processor/utils/eda_utils.py

import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from football_stream_processor.models.xg_model.feature_engineering import \
    add_engineered_features


class PassDataEDA:
    """
    Class for performing EDA on football pass data.

    :param df: The pandas DataFrame to analyze.
    :type df: pd.DataFrame
    :param resources_dir: Directory to save visualizations.
    :type resources_dir: str
    """

    def __init__(self, df: pd.DataFrame, resources_dir: str = "resources/plots"):
        self.df = df
        self.resources_dir = resources_dir
        os.makedirs(self.resources_dir, exist_ok=True)

    def missing_values(self, handle: str = None, fill_value=None) -> pd.Series:
        """
        Print and return missing value counts for each column.
        Optionally handle missing values by dropping or filling.

        :param handle: How to handle missing values: None (just report), 'drop' (drop rows), or 'fill' (fill with fill_value).
        :type handle: str or None
        :param fill_value: Value to fill missing values with if handle='fill'.
        :type fill_value: any
        :return: Series with missing value counts after handling.
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
        Displays and returns the distribution of classes in the specified target column.

        Prints the count and percentage of each unique value in the target column.
        If the column does not exist, prints an error message and returns an empty Series.

        :param target_col: The name of the target column to analyze (default is "pass_outcome").
        :type target_col: str, optional

        :returns: A Series containing the count of each unique value in the target column.
                  Returns an empty Series if the column is not found.
        :rtype: pd.Series
        """
        # Use logging module
        print("=== Class Distribution ===")
        if target_col in self.df.columns:
            counts = self.df[target_col].value_counts()
            print(counts)
            print("\nPercentage:")
            print(self.df[target_col].value_counts(normalize=True) * 100)
            return counts
        else:
            print(f"'{target_col}' column not found.")
            return pd.Series(dtype=int)

    def data_types(self) -> pd.Series:
        """
        Display and return the data types of all columns in the DataFrame.

        Prints the data types of each column and returns them as a pandas Series.

        :returns: A Series containing the data types of all columns.
        :rtype: pd.Series
        """
        print("\n=== Data Types ===")
        dtypes = self.df.dtypes
        print(dtypes)
        return dtypes

    def remove_duplicates(self) -> pd.DataFrame:
        """
        Detect and remove duplicate rows from the DataFrame.

        Prints the number of duplicate rows found. If any are found, they are removed.

        :returns: The DataFrame with duplicates removed.
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

    def eda_visualizations(self):
        """
        Generate and save basic exploratory data visualizations.

        Creates the following plots and saves them in the resources directory:
        - Heatmap of pass start locations
        - Heatmap of pass end locations
        - Violin plot of pass outcome vs. pass distance
        - Violin plot of pass outcome vs. pass angle
        - Scatter plot of distance vs. angle, colored by pass outcome

        Plots are saved as PNG files in the specified resources directory.
        """
        fig, axs = plt.subplots(1, 2, figsize=(16, 6))
        sns.kdeplot(x=self.df['start_x'], y=self.df['start_y'], fill=True, ax=axs[0])
        axs[0].set_title("Start Location Heatmap")
        axs[0].invert_yaxis()

        sns.kdeplot(x=self.df['end_x'], y=self.df['end_y'], fill=True, ax=axs[1])
        axs[1].set_title("End Location Heatmap")
        axs[1].invert_yaxis()
        plt.tight_layout()
        plt.savefig(os.path.join(self.resources_dir, "pass_location_heatmaps.png"))
        plt.close()

        fig = plt.figure(figsize=(8, 6))
        sns.violinplot(x="pass_outcome", y="distance", data=self.df)
        plt.title("Pass Success vs Distance")
        plt.savefig(os.path.join(self.resources_dir, "pass_success_vs_distance.png"))
        plt.close()

        fig = plt.figure(figsize=(8, 6))
        sns.violinplot(x="pass_outcome", y="angle", data=self.df)
        plt.title("Pass Success vs Angle")
        plt.savefig(os.path.join(self.resources_dir, "pass_success_vs_angle.png"))
        plt.close()

        fig = plt.figure(figsize=(10, 6))
        sns.scatterplot(x="angle", y="distance", hue="pass_outcome", data=self.df, alpha=0.4)
        plt.title("Distance vs Angle by Pass Outcome")
        plt.savefig(os.path.join(self.resources_dir, "distance_vs_angle_by_outcome.png"))
        plt.close()

        print(f"Visualizations saved in {self.resources_dir}")


def basic_checks(df: pd.DataFrame = None) -> pd.DataFrame:
    """
    Run basic EDA checks and return a cleaned DataFrame.

    :param df: DataFrame to check. If None, loads from default pickle.
    :type df: pd.DataFrame or None
    :return: Cleaned DataFrame.
    :rtype: pd.DataFrame
    """
    df = pd.read_pickle("~/projects/football_stream_processor/.pickle/pass_data.pkl") if df is None else df
    df = add_engineered_features(df)
    eda = PassDataEDA(df)
    eda.missing_values(handle="drop")
    df_clean = eda.remove_duplicates()
    return df_clean