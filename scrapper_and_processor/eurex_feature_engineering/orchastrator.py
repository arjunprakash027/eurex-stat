"""
This is where all the orchastration of the processor will be done.
"""
import pkgutil
import importlib
import pandas as pd

from eurex_feature_engineering.basetransformer import BaseTransformer
from typing import Any, List

def load_processors() -> None:

    """
    This method loads all the processors from the processor_1.py and other processor files.
    The processors should inherit from the BaseTransformer class.
    """
    # Dynamically load all the processors from the processor_1.py and other processor files - this is basically just using a import but dynamically
    pkg = importlib.import_module("eurex_feature_engineering")

    for a, name, b in pkgutil.iter_modules(pkg.__path__):
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
    
    # Add all the processors to the pipeline
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