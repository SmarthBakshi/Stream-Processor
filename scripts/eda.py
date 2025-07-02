"""
Exploratory Data Analysis (EDA) utilities for football pass data.

This module provides a class-based interface for common EDA tasks such as
missing value analysis, class imbalance checking, data type inspection, and duplicate removal.
"""
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
class PassDataEDA:
    """
    Class for performing EDA on football pass data.

    :param df: The pandas DataFrame to analyze.
    :type df: pd.DataFrame
    """

    def __init__(self, df: pd.DataFrame, resources_dir: str = "../resources"):
        self.df = df
        self.resources_dir = resources_dir
        os.makedirs(self.resources_dir, exist_ok=True)


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
    
    def eda_visualizations(self):
        """
        Generate and save EDA visualizations to the resources directory.
        """
        # Heatmaps of pass start and end locations
        fig, axs = plt.subplots(1, 2, figsize=(16, 6))
        sns.kdeplot(x=self.df['start_x'], y=self.df['start_y'], fill=True, ax=axs[0])
        axs[0].set_title("Start Location Heatmap")
        axs[0].invert_yaxis()

        sns.kdeplot(x=self.df['end_x'], y=self.df['end_y'], fill=True, ax=axs[1])
        axs[1].set_title("End Location Heatmap")
        axs[1].invert_yaxis()
        plt.tight_layout()
        heatmap_path = os.path.join(self.resources_dir, "pass_location_heatmaps.png")
        plt.savefig(heatmap_path)
        plt.close(fig)

        # Distance vs success
        fig = plt.figure(figsize=(8, 6))
        sns.violinplot(x="pass_outcome", y="distance", data=self.df)
        plt.title("Pass Success vs Distance")
        distance_path = os.path.join(self.resources_dir, "pass_success_vs_distance.png")
        plt.savefig(distance_path)
        plt.close(fig)

        # Angle vs success
        fig = plt.figure(figsize=(8, 6))
        sns.violinplot(x="pass_outcome", y="angle", data=self.df)
        plt.title("Pass Success vs Angle")
        angle_path = os.path.join(self.resources_dir, "pass_success_vs_angle.png")
        plt.savefig(angle_path)
        plt.close(fig)

        # 2D histogram of distance and angle
        fig = plt.figure(figsize=(10, 6))
        sns.scatterplot(x="angle", y="distance", hue="pass_outcome", data=self.df, alpha=0.4)
        plt.title("Distance vs Angle by Pass Outcome")
        scatter_path = os.path.join(self.resources_dir, "distance_vs_angle_by_outcome.png")
        plt.savefig(scatter_path)
        plt.close(fig)

        print(f"Visualizations saved in {self.resources_dir}")


def main():
    df = pd.read_pickle("../.pickle/pass_data.pkl") 
    eda = PassDataEDA(df)
    eda.missing_values()
    eda.class_distribution()
    eda.data_types()
    df_clean = eda.remove_duplicates()
    eda.eda_visualizations()

if __name__ == "__main__":
    main()