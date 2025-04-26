import sys
from scrapy.cmdline import execute
from eurex_feature_engineering.main import group_and_merge_data

def run_spider(
        spider_name: str
) -> None:
    
    """
    Just runs the spider 
    """
    print(f"Running spider : {spider_name}")
    execute(['scrapy','crawl',spider_name])

if __name__ == '__main__':
    spider = "recent_date_vacancy_spider"

    try:
        run_spider(
            spider_name=spider
            )
    except SystemExit as e:
        if e.code != 0:
            sys.exit(e.code)
    
    print("Running processing")

    group_and_merge_data()