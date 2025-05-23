"""
Calls the pipeline declaerd in orchastrator.py
Will primarily focus on providing the data to the pipeline and calling the pipeline
"""

import pandas as pd
from eurex_feature_engineering.orchastrator import run_pipeline
from typing import Any
import os
from eurex_feature_engineering.utils.stack_and_dedup import stack_and_dedup
from eurex_feature_engineering.utils.kaggle_utils import (
        download_dataset_from_kaggle,
        upload_dataset_to_kaggle
    )

# Attempt to import Kaggle utility functions
try:
    
    KAGGLE_UTILS_IMPORTED = True
    print("Successfully imported Kaggle utility functions.")
except ImportError as e:
    print(f"Warning: Failed to import Kaggle utility functions: {e}. Kaggle workflow will be disabled.")
    KAGGLE_UTILS_IMPORTED = False
    # Define dummy functions if import fails, to allow script to load if needed
    def download_dataset_from_kaggle(*args, **kwargs): print("DUMMY: download_dataset_from_kaggle called but not imported!"); return None
    def upload_dataset_to_kaggle(*args, **kwargs): print("DUMMY: upload_dataset_to_kaggle called but not imported!"); return False

# --- Kaggle Workflow Constants ---
KAGGLE_DATASET_SLUG = "arjunprakashrao/euraxess-full"
PROJECT_ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
KAGGLE_DOWNLOAD_PATH = os.path.join(PROJECT_ROOT_DIR, 'kaggle_download_temp_fe') # FE for Feature Engineering
TEMP_UPLOAD_CSV_PATH = os.path.join(KAGGLE_DOWNLOAD_PATH, 'merged_for_kaggle_upload_fe.csv')


def group_and_merge_data(enable_kaggle_workflow: bool = False) -> None:
    
    datasets = []
    original_kaggle_csv_name = None # To store the name of the downloaded Kaggle CSV
    kaggle_data_loaded_successfully = False

    if enable_kaggle_workflow:
        print("Kaggle workflow enabled.")
        if not KAGGLE_UTILS_IMPORTED:
            print("Error: Kaggle utilities not imported. Cannot proceed with Kaggle workflow.")
            # Fallback to local processing only
        else:
            os.makedirs(KAGGLE_DOWNLOAD_PATH, exist_ok=True)
            print(f"Attempting to download Kaggle dataset: {KAGGLE_DATASET_SLUG} to {KAGGLE_DOWNLOAD_PATH}")
            downloaded_kaggle_csv_file_path = download_dataset_from_kaggle(KAGGLE_DATASET_SLUG, KAGGLE_DOWNLOAD_PATH)

            if downloaded_kaggle_csv_file_path and os.path.exists(downloaded_kaggle_csv_file_path):
                original_kaggle_csv_name = os.path.basename(downloaded_kaggle_csv_file_path)
                print(f"Successfully downloaded Kaggle CSV: {downloaded_kaggle_csv_file_path} (Original name: {original_kaggle_csv_name})")
                try:
                    kaggle_df = pd.read_csv(downloaded_kaggle_csv_file_path, encoding="utf-8")
                    print(f"Read {len(kaggle_df)} rows from Kaggle CSV. Running transformations...")
                    kaggle_df = run_pipeline(kaggle_df) # Transform Kaggle data
                    datasets.append(kaggle_df)
                    kaggle_data_loaded_successfully = True
                    print(f"Processed and added data from Kaggle dataset.")
                except Exception as e:
                    print(f"Error processing downloaded Kaggle CSV {downloaded_kaggle_csv_file_path}: {e}")
                    # Fallback to local processing if Kaggle data processing fails
            else:
                print("Kaggle download failed or main CSV not found.")
                # Fallback will be handled below

    # Process daily files (newly scraped data) - this always happens
    daily_output_dir = "eurex_feature_engineering/output/daily"
    if not os.path.exists(daily_output_dir):
        print(f"Warning: Daily output directory not found: {daily_output_dir}. No new daily files to process.")
        daily_files = []
    else:
        daily_files = os.listdir(daily_output_dir)
        if not daily_files:
            print(f"No files found in daily output directory: {daily_output_dir}")

    print(f"Found {len(daily_files)} daily files to process from {daily_output_dir}.")
    for file in daily_files:
        try:
            daily_file_path = os.path.join(daily_output_dir, file)
            if not file.endswith(".csv"): # Skip non-CSV files
                print(f"Skipping non-CSV file: {daily_file_path}")
                continue
            print(f"Processing daily file: {daily_file_path}")
            df_current_date = pd.read_csv(daily_file_path, encoding="utf-8")
            if df_current_date.empty:
                print(f"Daily file {daily_file_path} is empty. Skipping.")
                continue
            df_current_date = run_pipeline(df_current_date)
            datasets.append(df_current_date)
            print(f"Processed and added data from daily file: {file}")
        except Exception as e:
            print(f"Error processing daily file {file}: {e}")
    
    # Fallback or standard local merge logic
    if not kaggle_data_loaded_successfully: # If Kaggle workflow was not enabled, or if it was enabled but failed
        print("Kaggle data not loaded or workflow disabled. Checking for existing local transformed data for merge.")
        previous_transformed_file = next(
                                    (p for p in [
                                        "eurex_feature_engineering/output/transformed/jobs_combined.csv",
                                        "eurex_feature_engineering/output/jobs.csv", # Older possible name
                                    ]
                                    if os.path.exists(p)
                                    ),
                                    None
                                )
        if previous_transformed_file:
            print(f"Found existing local transformed file: {previous_transformed_file}")
            try:
                previous_transformed_df = pd.read_csv(previous_transformed_file, encoding="utf-8")
                print(f"Read {len(previous_transformed_df)} rows from existing local file. Running transformations for consistency...")
                # To ensure consistency, always run transformations on the old base file as well
                previous_transformed_df = run_pipeline(previous_transformed_df)
                datasets.append(previous_transformed_df)
                print(f"Processed and added data from existing local transformed file.")
            except Exception as e:
                print(f"Error processing existing local transformed file {previous_transformed_file}: {e}")
        else:
            print("No existing local transformed file found to merge with daily data.")

    if not datasets:
        print("No data (neither Kaggle, daily, nor local previous) available to merge. Exiting.")
        return

    print(f"Preparing to merge {len(datasets)} dataset(s).")
    merged_df = stack_and_dedup(
        dfs = datasets,
        id_column = "job_id" # Ensure your stack_and_dedup uses a consistent ID column if possible.
                           # If 'job_id' doesn't exist in Kaggle data, this might need adjustment or
                           # ensure 'job_id' is created during transformation for all data sources.
    )
    
    # Ensure the main output directory exists
    main_output_dir = "eurex_feature_engineering/output/transformed"
    os.makedirs(main_output_dir, exist_ok=True)
    local_save_path = os.path.join(main_output_dir, "jobs_combined.csv")
    
    merged_df.to_csv(local_save_path, index=False)
    print(f"Processed and merged data saved locally to: {local_save_path} ({len(merged_df)} rows)")

    # Conditional Kaggle Upload
    if enable_kaggle_workflow:
        if not KAGGLE_UTILS_IMPORTED:
            print("Kaggle utilities not imported. Skipping Kaggle upload.")
        elif original_kaggle_csv_name is None:
            print("Original Kaggle CSV name not determined (download might have failed or was skipped). Skipping Kaggle upload.")
        else:
            print(f"Preparing to upload to Kaggle. Using temporary path: {TEMP_UPLOAD_CSV_PATH}")
            try:
                # Ensure KAGGLE_DOWNLOAD_PATH (used for temp_upload_csv and metadata) exists
                os.makedirs(KAGGLE_DOWNLOAD_PATH, exist_ok=True) 
                merged_df.to_csv(TEMP_UPLOAD_CSV_PATH, index=False)
                print(f"Data for upload saved to temporary file: {TEMP_UPLOAD_CSV_PATH}")

                version_notes = f"Automated update via eurex_feature_engineering/main.py on {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}"
                
                upload_success = upload_dataset_to_kaggle(
                    dataset_slug=KAGGLE_DATASET_SLUG,
                    base_download_folder=KAGGLE_DOWNLOAD_PATH, # Where dataset-metadata.json should be
                    updated_csv_path=TEMP_UPLOAD_CSV_PATH,
                    original_dataset_csv_name=original_kaggle_csv_name,
                    version_notes=version_notes
                )

                if upload_success:
                    print("Successfully uploaded updated dataset to Kaggle.")
                else:
                    print("Kaggle upload failed. Check logs from kaggle_utils.")
                
                # Clean up temporary upload file
                if os.path.exists(TEMP_UPLOAD_CSV_PATH):
                    os.remove(TEMP_UPLOAD_CSV_PATH)
                    print(f"Cleaned up temporary upload CSV: {TEMP_UPLOAD_CSV_PATH}")

            except Exception as e:
                print(f"An error occurred during Kaggle upload process: {e}")
        
    
if __name__ == "__main__":
    #group_and_merge_data(enable_kaggle_workflow=False)
    download_dataset_from_kaggle(KAGGLE_DATASET_SLUG, KAGGLE_DOWNLOAD_PATH)
