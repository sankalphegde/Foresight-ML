# Team Onboarding Checklist

Use this checklist to get up and running with the Foresight-ML project.

## Pre-Setup (Contact Team Lead)

- [ ] Receive Google Cloud Platform project access
- [ ] Obtain FRED API key (https://fred.stlouisfed.org/docs/api/)
- [ ] Get GitHub repository access
- [ ] Install required tools (Python 3.12, Docker, Git, gcloud CLI)

---

## Phase 1: Local Development Setup (30 minutes)

- [ ] Clone repository: `git clone <repo-url>`
- [ ] Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- [ ] Install dependencies: `uv sync`
- [ ] Copy env: `cp example.env .env`
- [ ] Add API keys to `.env` (FRED_API_KEY, SEC_USER_AGENT)
- [ ] Authenticate GCP: `gcloud auth application-default login`
- [ ] Set GCP project: `gcloud config set project financial-distress-ew`

---

## Phase 2: Cloud Setup (1 hour)

### Create Service Account
```bash
gcloud iam service-accounts create foresight-airflow \
  --display-name="Foresight ML Airflow"

gcloud projects add-iam-policy-binding financial-distress-ew \
  --member="serviceAccount:foresight-airflow@financial-distress-ew.iam.gserviceaccount.com" \
  --role="roles/run.invoker"

gcloud projects add-iam-policy-binding financial-distress-ew \
  --member="serviceAccount:foresight-airflow@financial-distress-ew.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

mkdir -p .gcp
gcloud iam service-accounts keys create .gcp/service-account-key.json \
  --iam-account=foresight-airflow@financial-distress-ew.iam.gserviceaccount.com
```

- [ ] Service account created
- [ ] Service account key downloaded to `.gcp/service-account-key.json`
- [ ] Permissions assigned (run.invoker, storage.admin)

### Build & Push Docker Images
```bash
# Setup Artifact Registry authentication
gcloud auth configure-docker us-central1-docker.pkg.dev

# Create repository (one-time, if not exists)
gcloud artifacts repositories create foresight \
  --repository-format=docker --location=us-central1

# Build & push via Cloud Build
gcloud builds submit --substitutions=_DOCKER_BUILDKIT=1
```

- [ ] Cloud Build completed successfully
- [ ] Both images pushed to Artifact Registry
- [ ] Images tagged as `fred:latest` and `sec:latest`

### Create Cloud Run Jobs
```bash
# FRED job
gcloud run jobs create foresight-ingestion \
  --image us-central1-docker.pkg.dev/financial-distress-ew/foresight/fred:latest \
  --region us-central1 --memory 2Gi --cpu 2 --task-timeout 3600s \
  --set-env-vars EXECUTION_DATE="$(date -u +%Y-%m-%dT%H:%M:%S)" \
  --set-env-vars GCS_BUCKET=financial-distress-data \
  --set-env-vars FRED_API_KEY=$(grep FRED_API_KEY .env | cut -d= -f2)

# SEC job
gcloud run jobs create foresight-sec-ingestion \
  --image us-central1-docker.pkg.dev/financial-distress-ew/foresight/sec:latest \
  --region us-central1 --memory 2Gi --cpu 2 --task-timeout 3600s \
  --set-env-vars EXECUTION_DATE="$(date -u +%Y-%m-%dT%H:%M:%S)" \
  --set-env-vars GCS_BUCKET=financial-distress-data \
  --set-env-vars SEC_USER_AGENT=$(grep SEC_USER_AGENT .env | cut -d= -f2)
```

- [ ] FRED ingestion job created
- [ ] SEC ingestion job created
- [ ] Both jobs have correct environment variables

### Test Cloud Run Jobs
```bash
gcloud run jobs execute foresight-ingestion --region us-central1
gcloud run jobs execute foresight-sec-ingestion --region us-central1
gcloud run jobs logs read foresight-ingestion --region us-central1 --limit 50
gcloud run jobs logs read foresight-sec-ingestion --region us-central1 --limit 50
```

- [ ] FRED job ran successfully
- [ ] SEC job ran successfully
- [ ] Data written to GCS

---

## Phase 3: Local Airflow Setup (30 minutes)

```bash
# Start services
docker-compose up postgres -d
docker-compose run --rm airflow-webserver airflow db init
docker-compose run --rm airflow-webserver airflow users create \
  --username admin --firstname Admin --lastname User \
  --role Admin --email admin@foresight.local --password admin
docker-compose up -d
```

- [ ] All Docker services running: `docker-compose ps`
- [ ] Airflow accessible at http://localhost:8080 (admin / admin)
- [ ] Scheduler is running and discovering DAGs
- [ ] DAG `foresight_ingestion` visible in UI

### Trigger DAG
1. Open http://localhost:8080
2. Find `foresight_ingestion` DAG
3. Click "Trigger DAG"
4. Monitor execution
5. Check Cloud Run jobs triggered successfully

- [ ] FRED task completed
- [ ] SEC task completed
- [ ] Data ingested to GCS

---

## Phase 4: Verify Everything Works

### Local Ingestion
```bash
uv run python -m src.ingestion.fred_job
uv run python -m src.ingestion.sec_job
```

- [ ] Both jobs run without errors locally

### Cloud Data
```bash
gsutil ls gs://financial-distress-data/raw/
gsutil ls gs://financial-distress-data/raw/fred/
gsutil ls gs://financial-distress-data/raw/sec/
```

- [ ] FRED data in `raw/fred/year=*/month=*/`
- [ ] SEC data in `raw/sec/year=*/quarter=*/`

### Airflow Logs
```bash
docker-compose logs -f airflow-scheduler
docker-compose logs -f airflow-webserver
```

- [ ] No errors in logs
- [ ] DAG executions visible in history

---

## Regular Development Tasks

### Running Tests
```bash
uv run pytest tests/
```

### Code Quality
```bash
uv run ruff format src/
uv run ruff check src/
uv run mypy src/
```

### Updating Docker Images
After code changes:
```bash
gcloud builds submit --substitutions=_DOCKER_BUILDKIT=1
gcloud run jobs update foresight-ingestion \
  --image us-central1-docker.pkg.dev/financial-distress-ew/foresight/fred:latest \
  --region us-central1
gcloud run jobs update foresight-sec-ingestion \
  --image us-central1-docker.pkg.dev/financial-distress-ew/foresight/sec:latest \
  --region us-central1
```

### Monitoring
```bash
# View Cloud Run job history
gcloud run jobs logs read foresight-ingestion --region us-central1

# View Airflow DAG executions
docker-compose exec airflow-webserver airflow dags list
docker-compose exec airflow-webserver airflow task-instances list

# Check GCS storage
gsutil du -h gs://financial-distress-data/
```

---

## Troubleshooting Quick Links

See **README.md** section "10. Troubleshooting" for:
- Airflow DAG not running
- Cloud Run job fails
- Docker build issues
- Permission errors
- General FAQ

---

## Useful Commands Reference

```bash
# Airflow
docker-compose logs -f airflow-scheduler         # Watch scheduler
docker-compose logs -f airflow-webserver         # Watch webserver
docker-compose ps                                 # Check service status
docker-compose down -v                            # Shutdown (remove volumes)

# Cloud Run
gcloud run jobs list --region us-central1        # List jobs
gcloud run jobs execute <job-name> --region us-central1  # Run manually
gcloud run jobs logs read <job-name> --region us-central1 --limit 100  # View logs
gcloud run jobs describe <job-name> --region us-central1  # See config

# GCS
gsutil ls gs://financial-distress-data/         # List contents
gsutil du -h gs://financial-distress-data/      # Storage usage
gsutil cp local.csv gs://financial-distress-data/  # Upload file

# Ingestion (Local)
uv run python -m src.ingestion.fred_job         # Run FRED locally
uv run python -m src.ingestion.sec_job          # Run SEC locally
```

---

## Next Steps After Setup

1. Read through the main **README.md** for full documentation
2. Explore `src/airflow/dags/foresight_ml_data_pipeline.py` to understand orchestration
3. Review FRED and SEC client implementations
4. Start working on feature engineering tasks
5. Set up scheduled DAG runs (weekly):
   ```bash
   gcloud run jobs update foresight-ingestion --schedule "0 2 * * 1" --region us-central1
   gcloud run jobs update foresight-sec-ingestion --schedule "0 3 * * 1" --region us-central1
   ```

---

## Contact & Support

- **Questions:** Refer to README.md documentation
- **Issues:** Create GitHub issue with error logs
- **Team Lead:** [Contact info]
- **Slack Channel:** #foresight-ml

---

**Setup Completion Time:** ~2 hours
**Estimated Date:** [Your start date + 2 hours]

Good luck! 🚀
