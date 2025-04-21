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

class TimeExtractors(BaseTransformer):
    
    is_transformation = True
    
    def extract_time_posted_on(
        self,
        time_str: str
    ) -> str:

        try:
            date_part = time_str.split("Posted on: ")[-1]
            return date_part
        except Exception as e:
            return '01 January 1901'

    def application_deadline_date(
        self,
        time_str: str
    ) -> str:

        try:
            date_part = time_str.split("-")[0].strip()
            return date_part
        except Exception as e:
            return '01 January 1901'
    
    def process(self, df:pd.DataFrame) -> pd.DataFrame:
    
        df['posted_on_date'] = df['posted_on'].apply(self.extract_time_posted_on)
        df['application_deadline_date'] = df['application_deadline'].apply(self.application_deadline_date)
        df['posted_on_date'] = pd.to_datetime(df['posted_on_date'], infer_datetime_format=True, errors='coerce')
        df['application_deadline_date'] = pd.to_datetime(df['application_deadline_date'], infer_datetime_format=True, errors='coerce')

        return df
