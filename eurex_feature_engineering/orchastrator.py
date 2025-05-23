"""
This is where all the orchastration of the processor will be done.
"""
# import os # Removed, if not used by core FE logic
import pandas as pd
# import logging # Reverted to print
import pkgutil
import importlib

from eurex_feature_engineering.basetransformer import BaseTransformer
from typing import Any, List # Reverted from Optional

# All Kaggle-specific imports, constants, helper functions, and workflow functions have been removed.

# --- Existing Feature Engineering Orchestration ---

def load_processors() -> None:

    """
    This method loads all the processors from the processor_1.py and other processor files.
    The processors should inherit from the BaseTransformer class.
    """
    # Dynamically load all the processors from the processor_1.py and other processor files - this is basically just using a import but dynamically
    pkg = importlib.import_module("eurex_feature_engineering.transformers")

    for _, name, _ in pkgutil.iter_modules(pkg.__path__): # Use _ for unused loop variables
        print(f"Loading processor: {name}")
        importlib.import_module(f"{pkg.__name__}.{name}")
    
    print(f"Loaded processors: {BaseTransformer.registry}")

def build_pipeline() -> List[BaseTransformer]:
    """
    This method builds the pipeline of processors to be used in the feature engineering process.
    The processors are defined in the processor_1.py and other processor files and should inherit from the BaseTransformer class.
    """
    load_processors()

    pipeline: List[BaseTransformer] = []
    
    for processor in BaseTransformer.registry:
        pipeline.append(processor())
    
    return pipeline

def run_pipeline(
        df: pd.DataFrame
) -> pd.DataFrame:
    """
    This method basically orchestrates the entire pipeline and runs the processors in the pipeline.
    """

    pipeline = build_pipeline()

    for transformer in pipeline:
        print(f"Running transformer: {transformer.__class__.__name__}")
        df = transformer(df)
    
    return df

# --- Main execution block ---
if __name__ == "__main__":
    # This block is a placeholder for testing or running the feature engineering pipeline directly.
    # For example, you might load a sample CSV, run the pipeline, and print/save the output.
    print("Orchestrator script executed. Defines feature engineering pipeline utilities.")
    
    # Example of how you might test the pipeline (requires a sample input file):
    # Define a sample input and output path for testing
    # SAMPLE_INPUT_CSV = "path/to/your/sample_input.csv" 
    # SAMPLE_OUTPUT_CSV = "path/to/your/sample_output.csv"

    # if os.path.exists(SAMPLE_INPUT_CSV): # os import would be needed here
    #     print(f"Loading sample data from: {SAMPLE_INPUT_CSV}")
    #     sample_df = pd.read_csv(SAMPLE_INPUT_CSV)
    #     print(f"Running feature engineering pipeline on sample data ({len(sample_df)} rows)...")
    #     transformed_sample_df = run_pipeline(sample_df)
    #     print(f"Pipeline completed. Transformed data has {len(transformed_sample_df)} rows.")
    #     # os.makedirs(os.path.dirname(SAMPLE_OUTPUT_CSV), exist_ok=True) # os import needed
    #     transformed_sample_df.to_csv(SAMPLE_OUTPUT_CSV, index=False)
    #     print(f"Transformed sample data saved to: {SAMPLE_OUTPUT_CSV}")
    # else:
    #     print(f"Sample input CSV not found at '{SAMPLE_INPUT_CSV}'. Cannot run example pipeline.")
    
    # For now, just a message indicating the script's purpose when run directly.
    pass
