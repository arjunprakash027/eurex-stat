"""
Utility functions for interacting with Kaggle.
"""
import os
import glob
import zipfile
import pandas as pd
import shutil
from datetime import datetime # For datetime.date, datetime.strptime
from typing import Optional, List, Any # Added Any for Dict[Any,Any] if needed, though not directly by these funcs

# logging can be useful for these utilities
import logging
# Configure logging if it's not already configured by the importing module
# A basic configuration if this module is run standalone or if no other config is set
if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    import kaggle
except (ImportError, OSError) as e:
    logging.warning(f"Kaggle library/API not configured: {e}. Kaggle functions will not work.")
    kaggle = None # Functions should check this or have their own try-except for import.

# --- Kaggle Utility Functions --- (Copied from eurex_scrapper/utils.py)

def download_dataset_from_kaggle(dataset_slug: str, download_path: str) -> Optional[str]:
    """
    Downloads dataset files from Kaggle, unzips them, and finds the main CSV and metadata.
    """
    global kaggle # Allow modification of the global kaggle variable if needed (e.g. for re-import)
    if kaggle is None:
        try:
            import kaggle as kg_api # Try to import it here if not available globally
            kaggle = kg_api 
        except (ImportError, OSError) as e:
            logging.error(f"Kaggle API not configured or library not found: {e}")
            return None
    
    try:
        # Clear existing download path more robustly
        if os.path.exists(download_path):
            logging.info(f"Clearing existing download path: {download_path}")
            for item in os.listdir(download_path):
                item_path = os.path.join(download_path, item)
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
        os.makedirs(download_path, exist_ok=True) # Ensure it exists after clearing or if new
        
        logging.info(f"Downloading dataset '{dataset_slug}' to '{download_path}'...")
        
        kaggle.api.dataset_download_files(dataset_slug, path=download_path, unzip=False) # Download without unzipping first
        
        # Determine expected zip file name from slug
        zip_file_name = dataset_slug.split('/')[-1] + '.zip'
        zip_file_path = os.path.join(download_path, zip_file_name)

        if not os.path.exists(zip_file_path):
            logging.warning(f"Expected zip file '{zip_file_path}' not found. Searching for any .zip file.")
            zip_files_found = glob.glob(os.path.join(download_path, '*.zip'))
            if not zip_files_found:
                logging.error(f"Error: No zip files found in download path: {download_path}")
                return None
            zip_file_path = zip_files_found[0] # Take the first one found
            logging.info(f"Found alternative zip file: {zip_file_path}")

        logging.info(f"Unzipping '{zip_file_path}' into '{download_path}'...")
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(download_path)
        
        try:
            os.remove(zip_file_path)
            logging.info(f"Removed zip file: {zip_file_path}")
        except OSError as e_rem:
            logging.warning(f"Could not remove zip file {zip_file_path}: {e_rem}")

        metadata_json_path = os.path.join(download_path, 'dataset-metadata.json')
        if not os.path.exists(metadata_json_path):
            logging.warning("Warning: dataset-metadata.json not found in the unzipped files.")
        else:
            logging.info(f"Found dataset-metadata.json at {metadata_json_path}")

        known_csv_name = "Euraxess_job_dataset_till_13_Nov_2023.csv" # As per previous spec
        preferred_csv_path = os.path.join(download_path, known_csv_name)

        if os.path.exists(preferred_csv_path):
            logging.info(f"Found preferred CSV file: {preferred_csv_path}")
            return preferred_csv_path
        else:
            logging.info(f"Preferred CSV '{known_csv_name}' not found. Searching for other *.csv files...")
        
        csv_files = glob.glob(os.path.join(download_path, '*.csv'))
        if not csv_files:
            logging.error(f"Error: No CSV files found in {download_path} after unzipping.")
            return None
        
        if len(csv_files) == 1:
            main_csv_path = csv_files[0]
            logging.info(f"Found single CSV file: {main_csv_path}")
            return main_csv_path
        
        logging.info(f"Multiple CSV files found and preferred CSV missing. Selecting the largest CSV file.")
        try:
            largest_csv = max(csv_files, key=lambda f: os.path.getsize(f)) #Requires os.path.getsize
            logging.info(f"Selected largest CSV: {largest_csv}")
            return largest_csv
        except Exception as e_size: # Catch any error during size comparison
            logging.error(f"Could not determine largest CSV by size (error: {e_size}), returning first found: {csv_files[0]}")
            return csv_files[0]

    except Exception as e: # Catch errors from kaggle API or other file operations
        logging.error(f"Error during Kaggle dataset download or processing for '{dataset_slug}': {e}", exc_info=True)
        return None

def get_latest_date_from_csv(csv_path: str, date_column: str) -> Optional[datetime.date]:
    """
    Reads a CSV, finds the latest date in a specified column.
    """
    if not os.path.exists(csv_path):
        logging.error(f"Error: CSV file not found at {csv_path}")
        return None
    try:
        df = pd.read_csv(csv_path)
        if df.empty:
            logging.info(f"CSV file '{csv_path}' is empty.") # Changed to info from print
            return None
        
        if date_column not in df.columns:
            logging.error(f"Error: Date column '{date_column}' not found in CSV '{csv_path}'. Available columns: {df.columns.tolist()}")
            return None

        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
        df.dropna(subset=[date_column], inplace=True)

        if df.empty:
            logging.info(f"No valid dates found in column '{date_column}' of CSV '{csv_path}' after parsing.") # Changed to info
            return None
            
        latest_date = df[date_column].max().date() 
        return latest_date
        
    except Exception as e:
        logging.error(f"Error reading or processing CSV '{csv_path}': {e}", exc_info=True)
        return None

def upload_dataset_to_kaggle(
    dataset_slug: str, 
    base_download_folder: str, 
    updated_csv_path: str,
    original_dataset_csv_name: str, # The name the CSV file should have in the Kaggle dataset
    version_notes: str
) -> bool:
    """
    Uploads the updated dataset (single CSV) to Kaggle.
    Manages a temporary folder for packaging.
    """
    global kaggle
    if kaggle is None:
        try:
            import kaggle as kg_api
            kaggle = kg_api
        except (ImportError, OSError) as e:
            logging.error(f"Kaggle API not configured or library not found: {e}")
            return False

    temp_upload_dir = os.path.join(base_download_folder, 'temp_upload_package_for_kaggle')
    
    try:
        if os.path.exists(temp_upload_dir):
            shutil.rmtree(temp_upload_dir)
        os.makedirs(temp_upload_dir, exist_ok=True)
        logging.info(f"Created temporary upload directory: {temp_upload_dir}")

        metadata_json_src_path = os.path.join(base_download_folder, 'dataset-metadata.json')
        if not os.path.exists(metadata_json_src_path):
            logging.error(f"Error: dataset-metadata.json not found in source folder '{base_download_folder}'. Cannot upload.")
            return False
        
        metadata_json_dest_path = os.path.join(temp_upload_dir, 'dataset-metadata.json')
        shutil.copy(metadata_json_src_path, metadata_json_dest_path)
        logging.info(f"Copied dataset-metadata.json to {metadata_json_dest_path}")

        if not os.path.exists(updated_csv_path):
            logging.error(f"Error: Updated CSV file to upload not found at '{updated_csv_path}'.")
            return False
        
        final_csv_dest_path = os.path.join(temp_upload_dir, original_dataset_csv_name)
        shutil.copy(updated_csv_path, final_csv_dest_path)
        logging.info(f"Copied updated CSV '{updated_csv_path}' to '{final_csv_dest_path}' for upload.")
        
        logging.info(f"Preparing to upload to Kaggle dataset (slug from metadata) from folder '{temp_upload_dir}'...")
        
        kaggle.api.dataset_create_version(
            folder=temp_upload_dir,
            version_notes=version_notes,
            quiet=False,
            dir_mode='zip' 
        )
        logging.info(f"Dataset version for '{dataset_slug}' uploaded to Kaggle successfully.")
        return True

    except Exception as e:
        logging.error(f"Error during Kaggle dataset upload for '{dataset_slug}': {e}", exc_info=True)
        return False
    finally:
        if os.path.exists(temp_upload_dir):
            logging.info(f"Cleaning up temporary upload directory: {temp_upload_dir}")
            shutil.rmtree(temp_upload_dir)

if __name__ == '__main__':
    logging.info("kaggle_utils.py executed directly. Contains Kaggle utility functions.")
    if kaggle:
        logging.info(f"Kaggle API client version: {getattr(kaggle.api, 'version', 'unknown')}") # Safe getattr
        # Basic test for download_dataset_from_kaggle (replace with a small, public dataset for actual testing)
        # TEST_SLUG = " próprio/small-public-dataset" # A real small public dataset slug
        # TEST_DOWNLOAD_DIR = "temp_kaggle_util_test"
        # logging.info(f"Attempting test download of {TEST_SLUG} to {TEST_DOWNLOAD_DIR}")
        # test_csv = download_dataset_from_kaggle(TEST_SLUG, TEST_DOWNLOAD_DIR)
        # if test_csv:
        #     logging.info(f"Test download successful: {test_csv}")
        #     # Test get_latest_date_from_csv (assuming 'date' column or similar exists in the test CSV)
        #     # latest_date = get_latest_date_from_csv(test_csv, "date_column_in_test_csv")
        #     # if latest_date:
        #     #     logging.info(f"Latest date in test CSV: {latest_date}")
        #     # else:
        #     #     logging.warning("Could not get latest date from test CSV.")
        #     if os.path.exists(TEST_DOWNLOAD_DIR):
        #         shutil.rmtree(TEST_DOWNLOAD_DIR)
        #         logging.info(f"Cleaned up test download directory: {TEST_DOWNLOAD_DIR}")
        # else:
        #     logging.error(f"Test download failed for {TEST_SLUG}.")
    else:
        logging.warning("Kaggle API client not available. Cannot run tests.")
