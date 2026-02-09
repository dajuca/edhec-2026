# BigQuery Extension (Optional)

Goal: teach a realistic “Modern Data Stack” pattern:
- **Docker** runs ingestion/transforms (compute)
- **BigQuery** stores curated datasets (warehouse)
- **Power BI** consumes BigQuery (semantic/visualization)

## Suggested flow (1 hour extension)
1. Create a BigQuery dataset (e.g., `bi_workshop`)
2. Create a service account with BigQuery write permissions
3. From a container (or local Python), extract from Postgres and load into BigQuery

### Student task idea
- Add a `dim_date` table
- Create an aggregated table `sales_daily_country`
- Load it into BigQuery
- Connect Power BI to BigQuery and build KPI cards + trends

> Keep secrets in `.env` and NEVER commit them.
