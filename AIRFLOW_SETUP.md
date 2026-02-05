# Local Airflow Setup

## Quick Start

```bash
# 1. Place your GCP service account key here
cp /path/to/service-account-key.json .gcp/service-account-key.json

# 2. Initialize Airflow database
docker-compose up postgres -d
docker-compose run --rm airflow-webserver airflow db init

# 3. Create Airflow user
docker-compose run --rm airflow-webserver airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@foresight.local \
  --password admin

# 4. Start all services
docker-compose up -d

# 5. Access Airflow UI
# Open http://localhost:8080
# Login with admin / admin
```

## Architecture

```
Airflow Scheduler (Local Docker)
    |
    ├── Weekly DAG: foresight_ingestion
    |   |
    |   ├── Task 1: run_fred_ingestion
    |   |   └── Executes: foresight-ingestion (Cloud Run Job)
    |   |
    |   └── Task 2: run_sec_ingestion
    |       └── Executes: foresight-sec-ingestion (Cloud Run Job)
    |
    └── (Future tasks for training, evaluation, etc.)
```

## Services

- **Postgres**: Metadata store for Airflow
- **Redis**: Message broker for Celery
- **Airflow Webserver**: UI on http://localhost:8080
- **Airflow Scheduler**: DAG orchestrator
- **Airflow Worker**: Celery executor

## Logs

```bash
# View logs
docker-compose logs -f airflow-scheduler
docker-compose logs -f airflow-webserver
docker-compose logs -f airflow-worker
```

## Shutdown

```bash
docker-compose down -v  # -v removes volumes (database)
```

## Environment

The services use:
- `GOOGLE_APPLICATION_CREDENTIALS`: Points to `.gcp/service-account-key.json`
- `GCP_PROJECT_ID`: `financial-distress-ew`
- DAG location: `src/airflow/dags/`

## Next Steps

Add downstream tasks to the DAG:
- Feature engineering
- Model training
- Model evaluation
- Prediction pipeline
