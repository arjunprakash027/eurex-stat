# Manage all the dependencies here
FROM python:3.13-slim as base
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Next stage with scrapper and processor
FROM python:3.13-slim as scrapper_and_processor
WORKDIR /app
COPY --from=base /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

WORKDIR /app
COPY . .

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]