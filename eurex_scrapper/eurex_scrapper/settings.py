# Scrapy settings for eurex_scrapper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "eurex_scrapper"

SPIDER_MODULES = ["eurex_scrapper.spiders"]
NEWSPIDER_MODULE = "eurex_scrapper.spiders"


# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 1

# Configure a delay for requests for the same website (default: 0)
DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 1

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}


# Enable and configure the AutoThrottle extension (disabled by default)
AUTOTHROTTLE_ENABLED = True
#The initial download delay
AUTOTHROTTLE_START_DELAY = 5
#The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 30
#The average number of requests Scrapy should be sending in parallel to
#each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 0.5
#Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = True

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

FEEDS = {
    'output/jobs.csv': {
        'format': 'csv',
        'overwrite': True,
        'encoding': 'utf-8',
    }
}


ITEM_PIPELINES = {
   "eurex_scrapper.pipelines.VacancyCleanerPipeline": 100,
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "eurex_scrapper.middlewares.EurexScrapperSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "eurex_scrapper.middlewares.EurexScrapperDownloaderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html