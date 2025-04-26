"""
This is a scrapy specific POC for extracting the data from the website
"""

import scrapy
from typing import Dict, Any

class POCSpider(scrapy.Spider):
    name = "poc_spider"

    base_url = 'https://euraxess.ec.europa.eu'
    start_urls = [
        f"{base_url}/jobs/search?page=1"
    ]

    def parse(self, response) -> Dict[str, Any]:

        print(f"Parsing page: {response.text}")
        return {}
