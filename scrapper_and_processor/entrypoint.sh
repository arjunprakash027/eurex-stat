#!/usr/bin/env bash

# Scrapper invoke
scrapy crawl recent_date_vacancy_spider

# Processor invoke
python3 -m eurex_feature_engineering.main


