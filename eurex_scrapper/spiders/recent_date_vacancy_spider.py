"""
Only scrape the data from the Euraxess website which is posted today
"""

import scrapy
from typing import Dict, Any, Generator, Union
from datetime import datetime
from scrapy.exceptions import CloseSpider
from eurex_scrapper.utils import lower_bound_date_check #type: ignore
class RecentDateSpider(scrapy.Spider):
    """
    This spider is a one time run spider that extracts all the data from the Euraxess website
    and saves it to a csv file

    There will also be an spider that runs extraction for every single day
    """

    name = "recent_date_vacancy_spider"

    base_url = 'https://euraxess.ec.europa.eu'
    start_urls = [
        f"{base_url}/jobs/search?sort%5Bname%5D=created&sort%5Bdirection%5D=DESC&page=0"
    ]

    # This is custom FEEDS only for this spider
    date = datetime.today().date().strftime("%Y-%m-%d")
    custom_settings = {
        'FEEDS': {
            f'eurex_feature_engineering/output/daily/jobs_{date}.csv': {
                'format': 'csv',
                'overwrite': True,
                'encoding': 'utf-8',
            }
        },
        'DOWNLOAD_DELAY': 10,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
    }

    # let this parse be a metadata extactor, for now the only metadata is the recent date
    def parse(self,
              response
              ) -> Generator[scrapy.Request, Any, Any]:

        print(f"Parsing page: {response.url}")

        page_number = 0

        # we are using a sorted list of pages based on date and therefore if there is a date that is not today, we will stop the entire process
        next_url = f"{self.base_url}/jobs/search?sort%5Bname%5D=created&sort%5Bdirection%5D=DESC&page={page_number}"

        seen_links = []

        # We scrape only the first page here and succussive pages will be scraped in the scrape_vacancy_data method of this class itself (recusrison to avoid infinite while loop)
        yield scrapy.Request(
            url=next_url,
            callback=self.scrape_vacancy_data,
            meta={
                "page_number": page_number,
                "seen_links": seen_links
            }
        )
        
    # This is where individual vacancy data for each page will be scraped
    def scrape_vacancy_data(self, 
                            response
                        ) -> Generator[Union[dict[str, Any], scrapy.Request], None, None]:
        

        print(f"Scraping next page : {response.url}")
        page_number = response.meta.get("page_number", 0)
        seen_links = response.meta.get("seen_links")

        # Extracting the vacancy data
        job_list = response.xpath('//*[@id="oe-list-container"]/div[3]/div/ul/li')
        
        for job in job_list:
            
            # extracting date from each job
            recent_date = job.xpath('.//article/div/ul[1]/li[2]/text()').get()

            # check if the date is today or not, if not raise and error and gracefully shutdown the spider
            if lower_bound_date_check(recent_date):

                vacancy_data = {
                "job_type": job.xpath('.//div/div[1]/ul/li[1]/span/text()').get(),
                "job_country": job.xpath('.//div/div[1]/ul/li[2]/span/text()').get(),
                "university": job.xpath('.//article/div/ul[1]/li[1]/a/text()').get(),
                "posted_on": job.xpath('.//article/div/ul[1]/li[2]/text()').get(),
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
                # raise an error and gracefully shutdown the spider
                raise CloseSpider(f"Job {recent_date}. Aborting...")
        
        next_page_number = page_number + 1
        next_url = f"{self.base_url}/jobs/search?sort%5Bname%5D=created&sort%5Bdirection%5D=DESC&page={next_page_number}"

        # We scrape only the first page here and succussive pages will be scraped in the scrape_vacancy_data method of this class itself (recusrison to avoid infinite while loop)
        yield scrapy.Request(
            url=next_url,
            callback=self.scrape_vacancy_data,
            meta={
                "page_number": next_page_number,
                "seen_links": seen_links
            }
        )