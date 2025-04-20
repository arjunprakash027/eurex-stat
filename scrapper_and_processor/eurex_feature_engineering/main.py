"""
Calls the pipeline declaerd in orchastrator.py
Will primarily focus on providing the data to the pipeline and calling the pipeline
"""

import pandas as pd
from eurex_feature_engineering.orchastrator import run_pipeline
from typing import Any
import os
from eurex_feature_engineering.utils.stack_and_dedup import stack_and_dedup

def run_transformations(
        recent: bool = False
) -> None:
    """
    This function performs transformation for all the data for entire timeline of job posting
    """

    if recent:
        recent_file = os.listdir("eurex_feature_engineering/output/daily")[-1]
        df_filename = f"daily/{recent_file}"
    else:
        df_filename = "jobs.csv"

    df = pd.read_csv(f"eurex_feature_engineering/output/{df_filename}", encoding="utf-8")

    transformed_df = run_pipeline(df)

    transformed_df.to_csv(f"eurex_feature_engineering/output/transformed/{df_filename}", index=False, encoding="utf-8")

    print(f"Transformed data saved to transformed/{df_filename}")

def group_and_merge_data() -> None:
    
    daily_files = os.listdir("eurex_feature_engineering/output/transformed/daily")
    previous_transformed_file = "eurex_feature_engineering/output/transformed/jobs_combined.csv" \
                                if os.path.exists("eurex_feature_engineering/output/transformed/jobs_combined.csv") \
                                else "eurex_feature_engineering/output/transformed/jobs.csv"
    
    datasets = []
    for file in daily_files:
        df_current_date = pd.read_csv(f"eurex_feature_engineering/output/transformed/daily/{file}")
        datasets.append(df_current_date)
    
    previous_transformed_df = pd.read_csv(previous_transformed_file)
    datasets.append(previous_transformed_df)
    
    merged_df = stack_and_dedup(
        dfs = datasets,
        id_column = "job_id"
    )
    
    merged_df.to_csv("eurex_feature_engineering/output/transformed/jobs_combined.csv")
    print(f"Transformed data saved to transformed/jobs_combined.csv")
        
    
if __name__ == "__main__":
    run_transformations(recent=True)
    run_transformations(recent=False)
    
    group_and_merge_data()

