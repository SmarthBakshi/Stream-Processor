# src/football_stream_processor/utils/eda_utils.py

import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from football_stream_processor.models.xg_model.feature_engineering import add_engineered_features


class PassDataEDA:
    def __init__(self, df: pd.DataFrame, resources_dir: str = "resources/plots"):
        self.df = df
        self.resources_dir = resources_dir
        os.makedirs(self.resources_dir, exist_ok=True)

    def missing_values(self) -> pd.Series:
        print("=== Missing Values ===")
        missing = self.df.isnull().sum()
        if missing.sum() > 0:
            print(missing[missing > 0])
        else:
            print("No missing values.\n")
        return missing

    def class_distribution(self, target_col: str = "pass_outcome") -> pd.Series:
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
        print("\n=== Data Types ===")
        dtypes = self.df.dtypes
        print(dtypes)
        return dtypes

    def remove_duplicates(self) -> pd.DataFrame:
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
    df = pd.read_pickle("~/projects/football_stream_processor/.pickle/pass_data.pkl") if df is None else df
    df = add_engineered_features(df)
    eda = PassDataEDA(df)
    eda.missing_values()
    df_clean = eda.remove_duplicates()
    return df_clean