"""
This module contains the function to stack and dedup the dataframes
"""

import pandas as pd

def stack_and_dedup(dfs: list[pd.DataFrame], id_column: str) -> pd.DataFrame:
    """
    Function to stack multiple dataframes and dedup it based on id_column
    """
    
    df = pd.concat(dfs, ignore_index=True)
    
    # Count duplicates based on id_column
    duplicate_counts = df[id_column].value_counts()
    print(duplicate_counts)
    #print(f"Number of unique IDs: {len(duplicate_counts)}")
    #print(f"Number of duplicate IDs: {len(df) - len(duplicate_counts)}")
    #print(f"Total number of rows: {len(df)}")
    #unique_df = df.drop_duplicates(subset=[id_column],keep="last")

    return df

