# Luxury BigQuery → ML Pipeline (Docker)

This repository shows an end‑to‑end **Dockerized** pipeline that:

1. **Authenticates with BigQuery** using a **Service Account JSON key mounted into the container**
2. **Queries** `edhec-01.luxurydata2502.price-monitoring-2022`
3. **Cleans + normalizes + splits** data
4. Trains a simple **ML model** to predict **price** from features (e.g., `collection`, `brand`, etc.)
5. **Creates a new BigQuery dataset on every run** and pushes:
   - the **cleaned dataset** (table: `cleaned_prices`)
   - **exchange rates** fetched from an API (table: `fx_rates_eur`)
6. Saves the trained model locally (`./models/model.joblib`)

---

## 0) Prerequisites

- Docker + Docker Compose
- A Google Cloud **Service Account key** (JSON) with BigQuery permissions

> **Do not commit service account keys to git.** Use the `secrets/` folder (gitignored).

---

## 1) Put your Service Account key in `secrets/`

Create this folder structure:

```
secrets/
  bq-sa.json
```

In this ChatGPT workspace, your uploaded key file is already available at:

- ` /mnt/data/9433b0f6-0c98-4e70-a67b-8f676e4ec57a.json `  (keep it private)  fileciteturn0file0

Copy it into the repo as:

```bash
mkdir -p secrets
cp /path/to/your/key.json secrets/bq-sa.json
```

---

## 2) Configure environment variables

Copy the example file and edit if needed:

```bash
cp .env.example .env
```

---

## 3) Run the pipeline

```bash
docker compose up --build
```

On each run, the pipeline will create a dataset like:

```
luxury_cleaned_YYYYMMDD_HHMMSS
```

and upload tables:

- `cleaned_prices`
- `fx_rates_eur`

---

## 4) Change the query

Edit `src/bq/query.py`:
- brand
- limit
- dataset/table names

---

## 5) Repo structure

```
.
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
├── secrets/                 # gitignored
├── models/
└── src/
    ├── main.py              # orchestrates the pipeline
    ├── bq/
    │   ├── client.py
    │   ├── query.py
    │   └── upload.py
    ├── fx/
    │   └── exchange_rates.py
    └── ml/
        ├── preprocess.py
        └── train.py
```

---

## Notes / Teaching points

- `.env` is read by **docker compose** (for variable substitution).  
- The Service Account key is passed via:
  - volume mount `./secrets/bq-sa.json:/secrets/bq-sa.json:ro`
  - env var `GOOGLE_APPLICATION_CREDENTIALS=/secrets/bq-sa.json`
- BigQuery uploads use `load_table_from_dataframe()` (schema inferred).


---

# API service for Power BI

This repo now includes a **FastAPI** service so you can connect **Power BI** to:

- raw BigQuery data
- cleaned data
- FX rates
- ML metrics
- ML predictions

## Run the API

```bash
docker compose up --build
```

API will be available at:

- `http://localhost:8000/docs` (Swagger UI)
- `http://localhost:8000/health`

### Run the pipeline (required once per container start)

In your browser (Swagger) or via curl:

```bash
curl -X POST "http://localhost:8000/run?limit=5000"
```

This will:
1) fetch from BigQuery
2) train model
3) create a new dataset `luxury_cleaned_YYYYMMDD_HHMMSS`
4) upload `cleaned_prices` and `fx_rates_eur`

## Endpoints to use in Power BI

After you call **POST** `/run`, these **GET** endpoints will return JSON:

- `GET /prices/raw`
- `GET /prices/cleaned`
- `GET /fx`
- `GET /ml/metrics`

### Example (Power BI)
Power BI Desktop → **Get Data** → **Web** → Advanced  
- URL: `http://localhost:8000/prices/cleaned`

Power BI will import JSON. You can then:
- Convert to table
- Expand records
- Refresh as needed (keep the container running)

### Prediction endpoint
- `GET /ml/predict?...` takes query parameters and returns a predicted price.

Example:

```
http://localhost:8000/ml/predict?price_before=10000&price_difference=0&price_percent_change=0&life_span_year=2025&life_span_month=12&brand=Cartier&currency=EUR&collection=LOVE&life_span=Q4%20December%202022
```

> Teaching note: for production-grade predictions, persist the preprocessing scalers/encoders. This repo keeps things simple on purpose.
