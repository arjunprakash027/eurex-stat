# eurex-stat

[Euraxess](https://euraxess.ec.europa.eu/jobs/search) is a European platform that connects researchers with job opportunities across universities, research institutions, and industry. It serves as a central hub for research-related career openings, covering multiple fields and countries. The platform is maintained by the European Commission and supports international mobility and career development for researchers.

This project is built around the goal of extracting and analyzing data from the Euraxess job portal to better understand academic hiring trends, demand across research fields, geographic distribution, and more.

## Quick Start – Run with Docker

You don’t need Python, Poetry, or any local dependencies.  
Simply pull the container from Docker Hub and run it; all outputs will land in a host-mounted folder of your choice.

```bash
docker run --rm -v "$(pwd)/data":/app/eurex_feature_engineering/output/transformed arjunrao123/eurex-stat:latest
```

* What happens:  
  1. The Scrapy spider crawls Euraxess and stores raw listings.  
  2. The processor cleans & enriches the data.  
  3. All CSV outputs appear in `./data` on your machine.

### Image details

* **Docker Hub:** <https://hub.docker.com/r/arjunrao123/eurex-stat>

The container removes itself after finishing (`--rm`), leaving only the data behind. Happy scraping!

## Project Overview

This repository is structured around three main goals:

1. **Data Collection**  
   Extract job listings from the Euraxess portal on a regular basis.

2. **Data Analysis** *(in progress)*  
   Apply statistical and exploratory methods to uncover patterns in the academic and research job market across Europe.

## Documentation

This repository includes multiple components, each with its own specific function. For technical details such as how the scrapers work or how to run the data pipeline, refer to the individual `README.md` files provided in the respective directories.

1) [Scrapper](https://github.com/arjunprakash027/eurex-stat/blob/main/scrapper_and_processor/README.md)
2) [Feature Engineering](https://github.com/arjunprakash027/eurex-stat/blob/main/scrapper_and_processor/eurex_feature_engineering/README.md)
