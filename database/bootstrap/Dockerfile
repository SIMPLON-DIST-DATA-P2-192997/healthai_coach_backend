FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY database/migrations/requirements.txt database/migrations/requirements.txt
COPY database/seed/requirements.txt database/seed/requirements.txt
RUN pip install --no-cache-dir \
    -r database/migrations/requirements.txt \
    -r database/seed/requirements.txt

COPY alembic.ini alembic.ini
COPY database/ database/
COPY dashboard/kpi_queries/ dashboard/kpi_queries/

ENTRYPOINT ["database/bootstrap/run_init.sh"]
