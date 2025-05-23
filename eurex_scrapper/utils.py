"""
Utility functions for the Euraxess scraper.
"""
# import os # No longer strictly needed by remaining functions
# import glob # No longer strictly needed
# import zipfile # No longer strictly needed
# import pandas as pd # No longer strictly needed
# import shutil # No longer strictly needed
from typing import Dict, Any, Optional, List # Optional and List might be removable if only for Kaggle funcs
import yaml
from datetime import datetime

# Kaggle import and related logic removed.

def read_config() -> Dict[Any,Any]:
    
    with open('eurex_scrapper/config.yaml') as config:
        conf_dict = yaml.safe_load(config)
    
    return conf_dict

def is_date_within_scrape_range(job_date_str: str, effective_start_date_str: str) -> bool:
    """
    Checks if a job's posting date is on or after a given effective start date.

    Args:
        job_date_str: The string representation of the job's posting date 
                      (e.g., "Posted on: 24 January 2024", "24 January, 2024").
        effective_start_date_str: The string representation of the earliest date 
                                  for jobs to be included (format "YYYY-MM-DD").

    Returns:
        True if the job_date is on or after effective_start_date, False otherwise.
        Returns False if date parsing fails for either input string.
    """
    try:
        # Parse effective_start_date_str (expected "YYYY-MM-DD")
        effective_start_date = datetime.strptime(effective_start_date_str, '%Y-%m-%d').date()
    except ValueError as e:
        print(f"Error parsing effective_start_date_str '{effective_start_date_str}': {e}. Cannot perform date comparison.")
        return False

    try:
        # Clean and parse job_date_str
        # Common cleaning: remove "Posted on:", strip whitespace, remove commas for flexibility
        cleaned_job_date_str = job_date_str.replace('Posted on:', '').replace(',', '').strip()
        
        # Attempt parsing with common formats. Start with "%d %B %Y" as it's common in Euraxess.
        job_date_obj = datetime.strptime(cleaned_job_date_str, '%d %B %Y').date()
        
    except ValueError:
        # Try another common format if the first fails, e.g., if month is abbreviated or order differs
        # For now, we'll stick to the primary known format and handle its failure.
        # A more robust solution might try a list of formats.
        print(f"Error parsing job_date_str '{job_date_str}' (cleaned: '{cleaned_job_date_str}') with format '%d %B %Y'.")
        return False
    except Exception as e: # Catch any other unexpected errors during job_date parsing
        print(f"An unexpected error occurred while parsing job_date_str '{job_date_str}': {e}")
        return False
    
    # Perform the comparison
    return job_date_obj >= effective_start_date


# Kaggle utility functions and the section marker "--- Kaggle Utility Functions ---" have been removed.
# The associated imports (glob, zipfile, pandas, shutil, and kaggle-specific try-except) have also been removed.

if __name__ == '__main__':
    # Example usage for is_date_within_scrape_range:
    print(f"--- Testing is_date_within_scrape_range ---")
    print(f"Job on 'Posted on: 12 April 2026' vs start '2023-01-01': {is_date_within_scrape_range('Posted on: 12 April 2026', '2023-01-01')}") 
    today_str_for_test = datetime.today().strftime('%Y-%m-%d')
    print(f"Job on 'Posted on: 12 April 2023' vs start '{today_str_for_test}': {is_date_within_scrape_range('Posted on: 12 April 2023', today_str_for_test)}") 
    current_date_euraxess_format = 'Posted on: ' + datetime.today().strftime('%d %B %Y')
    print(f"Job on '{current_date_euraxess_format}' vs start '{today_str_for_test}': {is_date_within_scrape_range(current_date_euraxess_format, today_str_for_test)}")
    print(f"Job on 'Invalid Date Format' vs start '{today_str_for_test}': {is_date_within_scrape_range('Invalid Date Format', today_str_for_test)}")
    print(f"Job on '{current_date_euraxess_format}' vs start 'Invalid-Start-Date': {is_date_within_scrape_range(current_date_euraxess_format, 'Invalid-Start-Date')}")
    print(f"Job on '24 January, 2024' vs start '2024-01-23': {is_date_within_scrape_range('24 January, 2024', '2024-01-23')}")
    print(f"Job on '24 January, 2024' vs start '2024-01-24': {is_date_within_scrape_range('24 January, 2024', '2024-01-24')}")
    print(f"Job on '24 January, 2024' vs start '2024-01-25': {is_date_within_scrape_range('24 January, 2024', '2024-01-25')}")

    # Removed example calls to Kaggle utility functions.
