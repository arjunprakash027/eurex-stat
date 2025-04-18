"""
Classes in here inherit from the base class BaseTransformer and implement the process method.
"""

from typing import Any
import pandas as pd
from eurex_feature_engineering.basetransformer import BaseTransformer

class IDTransformations(BaseTransformer):

    is_transformation = True

    def extract_job_id(self, job_link:str) -> str:
        """
        This method extracts the job id from the job link
        """
        return job_link.split("/")[-1]
    
    def process(self, df:pd.DataFrame) -> pd.DataFrame:

        """
        This method processes the input dataframe and returns the output dataframe
        """
        df["job_id"] = df["job_link"].apply(self.extract_job_id)
        df = df.set_index("job_id",drop=False)

        return df

