"""
Scraping the vacancy data from the Euraxess website. Use this scrapper to get the entire histroy that is present in euraxess website
"""

import scrapy
from typing import Dict, Any, Generator, Union

import scrapy.resolver
from scrapy.exceptions import CloseSpider

class VacancySpider(scrapy.Spider):
    """
    This spider is a one time run spider that extracts all the data from the Euraxess website
    and saves it to a csv file

    There will also be an spider that runs extraction for every single day
    """

    name = "vacancy_spider_scrape_all"

    base_url = 'https://euraxess.ec.europa.eu'
    start_urls = [
        f"{base_url}/jobs/search?page=1"
    ]

    # This is custom FEEDS only for this spider
    custom_settings = {
        'FEEDS': {
            'eurex_feature_engineering/output/jobs.csv': {
                'format': 'csv',
                #'overwrite': True,
                'encoding': 'utf-8',
            }
        },
        'DOWNLOAD_DELAY': 10,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
    } 

    # let this parse be a metadata extactor, for now the only metadata is the final number of web pages to scrape
    def parse(self, 
              response
              ) -> Generator[scrapy.Request, Any, Any]:

        # This is the xpath for final number
        final_number: str = response.xpath('//*[@id="oe-list-container"]/div[3]/div/nav/ul/li[7]/a/text()').get()
        final_number_int: int = int(final_number.strip()) if final_number else 0

        print(f"Final number: {final_number_int}")
        print(f"Parsing page: {response.url}")
        page_number = 0
        
        # We go through every page and scrape the data using scrape_vacancy_data method of this class itself
        next_url = f"{self.base_url}/jobs/search?page={page_number}"
        
        seen_links = []
        
        yield scrapy.Request(
            url=next_url,
            callback=self.scrape_vacancy_data,
            meta={
                "page_number": page_number,
                "final_page_number": final_number_int,
                "seen_links": seen_links
            }
        )
            
    # This is where individual vacancy data for each page will be scraped
    def scrape_vacancy_data(self, 
                            response
                        ) -> Generator[Union[Dict[str,Any],scrapy.Request], None, None]:
        
        
        print(f"Scraping next page : {response.url}")
        
        page_number = response.meta.get("page_number")
        final_page_number = response.meta.get("final_page_number")
        seen_links = response.meta.get("seen_links")

        # Extracting the vacancy data
        job_list = response.xpath('//*[@id="oe-list-container"]/div[3]/div/ul/li')
        
        for job in job_list:
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
                raise CloseSpider(f"Seen a repeat of job ids at this page link : {response.url}")
            
            seen_links.append(vacancy_data["job_link"])

            yield vacancy_data
        
        if page_number < final_page_number:
            page_number += 1
            next_url = f"{self.base_url}/jobs/search?page={page_number}"
            
            yield scrapy.Request(
                url=next_url,
                callback=self.scrape_vacancy_data,
                meta={
                    "page_number": page_number,
                    "final_page_number": final_page_number,
                    "seen_links": seen_links
                    }
            )