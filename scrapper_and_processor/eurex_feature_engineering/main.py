"""
Calls the pipeline declaerd in orchastrator.py
Will primarily focus on providing the data to the pipeline and calling the pipeline
"""

import pandas as pd
from eurex_feature_engineering.orchastrator import run_pipeline
from typing import Any
import os
from eurex_feature_engineering.utils.stack_and_dedup import stack_and_dedup


def group_and_merge_data() -> None:
    
    daily_files = os.listdir("eurex_feature_engineering/output/daily")
    previous_transformed_file = "eurex_feature_engineering/output/transformed/jobs_combined.csv" \
                                if os.path.exists("eurex_feature_engineering/output/transformed/jobs_combined.csv") \
                                else "eurex_feature_engineering/output/jobs.csv"
    
    datasets = []
    for file in daily_files:
        try:
            df_current_date = pd.read_csv(f"eurex_feature_engineering/output/daily/{file}",encoding="utf-8")
            df_current_date = run_pipeline(df_current_date)
            datasets.append(df_current_date)
        except Exception as e:
            print(f"Error on processing {file} : {e}")
    
    previous_transformed_df = pd.read_csv(previous_transformed_file, encoding="utf-8")
    # to ensure the previous transformed file has the same updated transformations if any, we run the transformations on it again to ensure that. None of the transformations delete any column and therefore I think it is fine to do this
    previous_transformed_df = run_pipeline(previous_transformed_df)

    datasets.append(previous_transformed_df)
    
    merged_df = stack_and_dedup(
        dfs = datasets,
        id_column = "job_id"
    )
    
    merged_df.to_csv("eurex_feature_engineering/output/transformed/jobs_combined.csv", index=False)
    print(f"Transformed data saved to transformed/jobs_combined.csv")
        
    
if __name__ == "__main__":
    group_and_merge_data()

