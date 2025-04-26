# Manage all the dependencies here
FROM python:3.11-slim as builder

# Wheel the dependencies
RUN apt-get update && \
    apt-get install --no-install-recommends -y build-essential && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /src
COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

# Distroless runtime image
FROM gcr.io/distroless/python3-debian12
LABEL  org.opencontainers.image.title="eurex-stat" \
       org.opencontainers.image.description="Daily scraping & processing for Eurex data" \
       org.opencontainers.image.source="https://github.com/arjunprakash027/eurex-stat" \
       org.opencontainers.image.licenses="MIT"\
       org.opencontainers.image.documentation="https://github.com/arjunprakash027/eurex-stat" \
       org.opencontainers.image.source="https://github.com/arjunprakash027/eurex-stat" \
       maintainer="Arjun Prakash" \
       org.opencontainers.image.authors="Arjun Prakash <arjunprakash027@gmail.com>"

COPY --from=builder /install /usr/local
WORKDIR /app

ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages:$PYTHONPATH

COPY eurex_feature_engineering ./eurex_feature_engineering
COPY eurex_scrapper ./eurex_scrapper
COPY scrapy.cfg .
COPY entrypoint.py . 
USER nobody
ENTRYPOINT ["python3","/app/entrypoint.py"]