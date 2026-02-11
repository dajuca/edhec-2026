from google.cloud import bigquery
import pandas as pd

from src.bq.client import get_bq_client


QUERY_TEMPLATE = """
SELECT
  uid, brand, url, price, currency, image_url, collection, reference_code,
  life_span_date, life_span, price_before, price_difference, price_percent_change, price_changed
FROM `{project_id}.{dataset_id}.{table_id}`
WHERE brand = @brand
ORDER BY life_span_date DESC
LIMIT @limit
"""


def fetch_prices(
    project_id: str,
    dataset_id: str,
    table_id: str,
    brand: str,
    limit: int = 10,
) -> pd.DataFrame:
    client = get_bq_client(project_id)

    query = QUERY_TEMPLATE.format(project_id=project_id, dataset_id=dataset_id, table_id=table_id)

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("brand", "STRING", brand),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
    )

    job = client.query(query, job_config=job_config)
    df = job.result().to_dataframe()
    return df
