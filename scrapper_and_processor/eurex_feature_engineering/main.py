"""
Calls the pipeline declaerd in orchastrator.py
Will primarily focus on providing the data to the pipeline and calling the pipeline
"""

import pandas as pd
from eurex_feature_engineering.orchastrator import run_pipeline
from typing import Any
import os

def run_transformations(
        recent: bool = False
) -> None:
    """
    This function performs transformation for all the data for entire timeline of job posting
    """

    if recent:
        recent_file = os.listdir("eurex_feature_engineering/output/daily")[0]
        df_filename = f"daily/{recent_file}"
    else:
        df_filename = "jobs.csv"

    df = pd.read_csv(f"eurex_feature_engineering/output/{df_filename}", encoding="utf-8")

    transformed_df = run_pipeline(df)

    transformed_df.to_csv(f"eurex_feature_engineering/output/transformed/{df_filename}", index=False, encoding="utf-8")

    print(f"Transformed data saved to transformed/{df_filename}")

if __name__ == "__main__":
    # Run the transformations
    run_transformations(recent=True)
    run_transformations(recent=False)

