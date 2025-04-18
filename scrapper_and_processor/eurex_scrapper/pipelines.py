# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import re
from typing import Dict, Any
class EurexScrapperPipeline:
    def process_item(self, item, spider):
        return item

class VacancyCleanerPipeline:

    def process_item(self, item: Dict[str,str], spider) -> Dict[str,str]:
        """
        Data passes throguh this pipeline before getting saved to the csv file, so we clean it in here
        """        
        for key, value in item.items():
            item[key] = self.clean_text(value)
        
        return item

    @staticmethod
    def clean_text(text: str) -> str:
        """
        This actaully has the cleaning logic
        """
        if text is None:
            return ""
        
        # These stuffs might break the csv file, therefore we need to remove them
        text = text.replace('\n', ' ').replace('\r', ' ').replace('"', '').replace(',', '')
        return re.sub(r'\s+', ' ', text).strip()