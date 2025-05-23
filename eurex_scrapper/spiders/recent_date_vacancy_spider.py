"""
Scrapes job data from Euraxess from a specified start date.
"""

import os
# import yaml # Removed as config loading is simplified
import scrapy
from typing import Dict, Any, Generator, Union # Keep existing relevant typing imports
from datetime import datetime, timedelta # Add timedelta
# import pandas as pd # Removed as it's not used after Kaggle logic removal
from scrapy.exceptions import CloseSpider

from eurex_scrapper.utils import (
    # download_dataset_from_kaggle, # Removed
    # get_latest_date_from_csv, # Removed
    # upload_dataset_to_kaggle, # Removed
    is_date_within_scrape_range 
)

class RecentDateSpider(scrapy.Spider):
    """
    This spider is a one time run spider that extracts all the data from the Euraxess website
    and saves it to a csv file

    There will also be an spider that runs extraction for every single day
    """

    name = "recent_date_vacancy_spider"
    base_url = 'https://euraxess.ec.europa.eu'

    def __init__(self, start_date=None, *args, **kwargs): # Renamed start_date_arg back to start_date for clarity with -a
        super(RecentDateSpider, self).__init__(*args, **kwargs)
        self.logger.info("Initializing RecentDateSpider (Simplified for non-Kaggle operation)...")

        effective_start_date_str = None
        config_cutoff_date_str = None # YYYY-MM-DD from config

        # --- Load cutoff_date from config.yaml ---
        try:
            config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.yaml'))
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    if config and 'cutoff_date' in config:
                        raw_cutoff_date = config['cutoff_date']
                        if isinstance(raw_cutoff_date, str):
                            if raw_cutoff_date.lower() == 'today':
                                config_cutoff_date_str = datetime.today().strftime('%Y-%m-%d')
                            else: # Attempt to parse DD-MM-YYYY or YYYY-MM-DD
                                try:
                                    config_cutoff_date_str = datetime.strptime(raw_cutoff_date, '%d-%m-%Y').strftime('%Y-%m-%d')
                                except ValueError:
                                    try:
                                        datetime.strptime(raw_cutoff_date, '%Y-%m-%d') # Validate
                                        config_cutoff_date_str = raw_cutoff_date
                                    except ValueError:
                                        self.logger.warning(f"Invalid date format '{raw_cutoff_date}' in config.yaml for cutoff_date. Using 'today'.")
                                        config_cutoff_date_str = datetime.today().strftime('%Y-%m-%d')
                        else:
                            self.logger.warning(f"cutoff_date in config.yaml is not a string: '{raw_cutoff_date}'. Using 'today'.")
                            config_cutoff_date_str = datetime.today().strftime('%Y-%m-%d')
                    else:
                        self.logger.info("config.yaml is empty or cutoff_date not found. Using 'today' as default cutoff.")
                        config_cutoff_date_str = datetime.today().strftime('%Y-%m-%d')
            else:
                self.logger.info(f"config.yaml not found at {config_path}. Using 'today' as default cutoff.")
                config_cutoff_date_str = datetime.today().strftime('%Y-%m-%d')
        except Exception as e:
            self.logger.error(f"Error loading or parsing config.yaml for cutoff_date: {e}. Using 'today' as default.")
            config_cutoff_date_str = datetime.today().strftime('%Y-%m-%d')

        self.logger.info(f"Configured cutoff_date (from config.yaml or default 'today'): {config_cutoff_date_str}")

        # --- Determine effective_start_date ---
        if start_date: # User-provided -a start_date=YYYY-MM-DD
            self.logger.info(f"Command-line argument 'start_date' provided: {start_date}")
            try:
                datetime.strptime(start_date, "%Y-%m-%d") # Validate format
                effective_start_date_str = start_date
                self.logger.info(f"Using command-line start_date: {effective_start_date_str}")
            except ValueError:
                self.logger.warning(f"Invalid format for command-line 'start_date={start_date}'. Expected YYYY-MM-DD. Defaulting to config cutoff_date: {config_cutoff_date_str}")
                effective_start_date_str = config_cutoff_date_str
        else:
            self.logger.info(f"No command-line 'start_date' provided. Using config cutoff_date: {config_cutoff_date_str}")
            effective_start_date_str = config_cutoff_date_str
        
        # Convert to date object and back to string to ensure consistent format and store
        try:
            effective_start_date_obj = datetime.strptime(effective_start_date_str, "%Y-%m-%d").date()
            self.start_date_param = effective_start_date_obj.strftime("%Y-%m-%d")
        except ValueError: # Should ideally not happen if logic above is correct, but as a safeguard
            self.logger.error(f"Failed to parse final effective_start_date_str '{effective_start_date_str}'. Defaulting to today.")
            self.start_date_param = datetime.today().strftime("%Y-%m-%d")

        self.logger.info(f"Effective start date for scraping (self.start_date_param): {self.start_date_param}")
        
        # --- Custom Settings & Output Path ---
        # Output path relative to where `scrapy crawl` is executed.
        # If run from `eurex_scrapper/`, this will create output at `eurex_scrapper/eurex_feature_engineering/output/daily/`
        self.relative_output_csv_filename = os.path.join(
            'eurex_feature_engineering', 'output', 'daily', f'jobs_{self.start_date_param}.csv'
        )
        # Note: self.output_csv_path (absolute path) is not strictly needed if `closed` method is removed.
        # However, FEEDS setting uses the relative path.

        self.custom_settings = {
            'FEEDS': {
                self.relative_output_csv_filename: { 
                    'format': 'csv', 
                    'overwrite': True, 
                    'encoding': 'utf-8',
                }
            },
            'DOWNLOAD_DELAY': 10, 
            'RANDOMIZE_DOWNLOAD_DELAY': True,
            'CONCURRENT_REQUESTS': 1, 
            'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
            'LOG_LEVEL': 'INFO', # Ensure self.logger.info messages are visible
        }

    # start_urls is removed as start_requests is used.

    def start_requests(self) -> Generator[scrapy.Request, Any, Any]:
        initial_url = f"{self.base_url}/jobs/search?sort%5Bname%5D=created&sort%5Bdirection%5D=DESC&page=0"
        self.logger.info(f"Starting scrape with initial URL: {initial_url}")
        yield scrapy.Request(
            url=initial_url,
            callback=self.scrape_vacancy_data,
            meta={"page_number": 0, "seen_links": []} 
        )
        
    def scrape_vacancy_data(self, response) -> Generator[Union[dict[str, Any], scrapy.Request], None, None]:
        self.logger.info(f"Scraping page: {response.url}")
        page_number = response.meta.get("page_number", 0)
        seen_links = response.meta.get("seen_links", []) 

        job_list = response.xpath('//*[@id="oe-list-container"]/div[3]/div/ul/li')
        
        if not job_list:
            self.logger.info(f"No jobs found on page {response.url}. This might be the end of results or an issue with page content.")
            return

        job_found_on_page = False 
        for job in job_list:
            
            # extracting date from each job
            job_posted_date_str = job.xpath('.//article/div/ul[1]/li[2]/text()').get() # Use a more descriptive name

            if not job_posted_date_str:
                self.logger.warning(f"Could not extract job posted date for a job on {response.url}. Skipping item.")
                continue # Skip this item if date is missing

            # check if the date is within the scrape range
            if is_date_within_scrape_range(job_posted_date_str, self.start_date_param):

                vacancy_data = {
                "job_type": job.xpath('.//div/div[1]/ul/li[1]/span/text()').get(),
                "job_country": job.xpath('.//div/div[1]/ul/li[2]/span/text()').get(),
                "university": job.xpath('.//article/div/ul[1]/li[1]/a/text()').get(),
                "posted_on": job_posted_date_str, # Use the extracted and validated date string
                "job_title": job.xpath('.//h3/a/span/text()').get(),
                "job_link": response.urljoin(job.xpath('.//h3/a/@href').get()),
                "job_description": job.xpath('.//div[@class="ecl-content-block__description"]/p/text()').get(),
                "department": job.xpath('.//div[contains(@class,"id-Department")]//div[2]/text()').get(),
                "job_location": job.xpath('.//div[contains(@class,"id-Work-Locations")]//div[2]/text()').get(),
                "job_field": ' '.join(job.xpath('.//div[contains(@class,"id-Research-Field")]//text()').getall()).strip(),
                "job_profile": ' '.join(job.xpath('.//div[contains(@class,"id-Researcher-Profile")]//text()').getall()).strip(),
                "funding_program": job.xpath('.//div[contains(@class,"id-Funding-Programme")]//a/text()').get(),
                "application_deadline": job.xpath('.//div[contains(@class,"id-Application-Deadline")]//time/text()').get(),
                "origin_page": response.url
            }

                if vacancy_data["job_link"] in seen_links:
                    # todo : repeat the same page after some delay instead of throwing an error
                    raise CloseSpider(f"Seen a repeat of job ids at this page link : {response.url}")
                
                seen_links.append(vacancy_data["job_link"])

                yield vacancy_data

            else:
                # Log the date that was out of range and then raise CloseSpider
                self.logger.info(f"Job with posted date '{job_posted_date_str}' is before effective start date '{self.start_date_param}'. Stopping scrape for this page/spider.")
                raise CloseSpider(f"Job date {job_posted_date_str} is before effective start date {self.start_date_param}. Aborting...")
        
        if not job_found_on_page and page_number == 0: 
             self.logger.info(f"No jobs on the first page ({response.url}) met the date criteria '{self.start_date_param}'. Spider will stop.")
             return 

        if job_found_on_page: 
            next_page_number = page_number + 1
            next_url = f"{self.base_url}/jobs/search?sort%5Bname%5D=created&sort%5Bdirection%5D=DESC&page={next_page_number}"
            self.logger.info(f"Requesting next page: {next_url}")
            yield scrapy.Request(
                url=next_url,
                callback=self.scrape_vacancy_data,
                meta={"page_number": next_page_number, "seen_links": seen_links}
            )
        else: 
            self.logger.info(f"No jobs on page {response.url} were within the date range after processing all items. Assuming end of relevant results.")

    # The 'closed' method has been removed as Kaggle integration is no longer part of this spider.
    # Standard Scrapy 'closed' signal can still be connected to if needed for other purposes,
    # but the custom Kaggle logic is gone.
    def closed(self, reason):
        self.logger.info(f"Spider closed: {reason}. Output data should be in {self.relative_output_csv_filename}")
        # Call the parent's closed method if it has any specific Scrapy cleanup.
        super(RecentDateSpider, self).closed(reason)
