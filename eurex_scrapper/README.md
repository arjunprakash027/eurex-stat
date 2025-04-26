# 🕷️ Euraxess Job Scraper

This project scrapes academic and research job postings from the [Euraxess](https://euraxess.ec.europa.eu/jobs/search) website using **Scrapy** and stores structured job data for downstream analysis.

---

## 📁 Project Structure

```
.
├── eurex_scrapper/              # Scrapy project core (spiders, pipelines, settings)
│   ├── spiders/
│   │   ├── vacancy_data_extractor.py           # Scrapes all job pages
│   │   └── recent_date_vacancy_spider.py       # Scrapes only jobs posted today
│   ├── items.py
│   ├── pipelines.py
│   ├── middlewares.py
│   ├── settings.py
│
├── eurex_feature_engineering/   # Stores post-scraping output
│   └── output/
│       ├── jobs.csv                     # Latest scraped jobs (overwrite)
│       └── daily/jobs_YYYY-MM-DD.csv    # Timestamped daily job dumps
│
├── scrapy.cfg
├── requirements.txt
└── README.md
```

---

## 🧠 Spiders Overview

### 🔹 `vacancy_data_extractor.py` (`vacancy_spider_scrape_all`)
Scrapes **all available job listings** on the Euraxess job portal, starting from the most recent and going page-by-page until older job dates are reached.

### 🔹 `recent_date_vacancy_spider.py` (`recent_date_vacancy_spider`)
Scrapes **only the jobs posted today**, and stops crawling as soon as it detects an older job listing. Optimized for daily runs.

---

## 💾 Output Location

All scraped job listings are saved under:

```
eurex_feature_engineering/output/
```

- `jobs.csv`: Latest run output (overwritten on every run)
- `daily/jobs_YYYY-MM-DD.csv`: Daily archive with timestamp

---

## 🛠️ Notable Project Customizations

The following Scrapy settings were customized per spider to enable proper handling:

- **Per-spider feed export** using `custom_settings['FEEDS']`
- **Graceful shutdown** on old data using `CloseSpider`
- **Recursive pagination** to ensure efficient and controlled crawling
- **Data cleaning** handled via `pipelines.py` to remove newline characters, commas, and unnecessary whitespace

---

## 🚀 How to Run

### 🐍 1. Install Dependencies

Make sure you have Python 3.10+ and install all dependencies:

```bash
pip install -r requirements.txt
```

### 🕷️ 2. Run Spiders

#### Scrape only today's jobs:
```bash
scrapy crawl recent_date_vacancy_spider
```

#### Scrape all jobs for all the data present in euraxess:
```bash
scrapy crawl vacancy_spider_scrape_all
```

---

## ✅ Requirements

- Python 3.10+
- Scrapy 2.11+
- Internet access (obviously 😄)

---