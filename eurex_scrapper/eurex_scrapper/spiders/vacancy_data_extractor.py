"""
Scraping the vacancy data from the Euraxess website.
"""

import scrapy
from typing import Dict, Any, Generator

class VacancySpider(scrapy.Spider):
    name = "vacancy_spider"

    base_url = 'https://euraxess.ec.europa.eu'
    start_urls = [
        f"{base_url}/jobs/search?page=1"
    ]


    # let this parse be a metadata extactor, for now the only metadata is the final number of web pages to scrape
    def parse(self, 
              response
              ) -> Generator[scrapy.Request, Any, Any]:

        # This is the xpath for final number
        final_number: str = response.xpath('//*[@id="oe-list-container"]/div[3]/div/nav/ul/li[7]/a/text()').get()
        final_number_int: int = int(final_number.strip()) if final_number else 0

        print(f"Final number: {final_number_int}")
        print(f"Parsing page: {response.url}")

        final_number_int = 100

        # We go through evewry page and scrape the data using scrape_vacancy_data method of this class itself
        for page_number in range(0, final_number_int):
            next_url = f"{self.base_url}/jobs/search?page={page_number}"
            yield scrapy.Request(
                url=next_url,
                callback=self.scrape_vacancy_data,
                meta={
                    "page_number": page_number
                }
            )
            
    # This is where individual vacancy data for each page will be scraped
    def scrape_vacancy_data(self, 
                            response
                        ) -> Generator[dict[str, Any], Any, Any]:
        
        
        print(f"Scraping next page : {response.url}")

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
            "job_profile": job.xpath('.//div[contains(@class,"id-Researcher-Profile")]//a/text()').get(),
            "funding_program": job.xpath('.//div[contains(@class,"id-Funding-Programme")]//a/text()').get(),
            "application_deadline": job.xpath('.//div[contains(@class,"id-Application-Deadline")]//time/text()').get(),
        }

            yield vacancy_data