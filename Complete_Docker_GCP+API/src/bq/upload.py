from google.cloud import bigquery
from google.api_core.exceptions import Conflict
import pandas as pd

from src.bq.client import get_bq_client


def create_dataset(project_id: str, dataset_id: str, location: str = "EU") -> None:
    client = get_bq_client(project_id)
    dataset_ref = bigquery.Dataset(f"{project_id}.{dataset_id}")
    dataset_ref.location = location

    try:
        client.create_dataset(dataset_ref)
        print(f"Created dataset: {project_id}.{dataset_id} (location={location})")
    except Conflict:
        print(f"Dataset already exists: {project_id}.{dataset_id} (location={location})")


def upload_dataframe(
    project_id: str,
    dataset_id: str,
    table_id: str,
    df: pd.DataFrame,
    write_disposition: str = "WRITE_TRUNCATE",
) -> None:
    client = get_bq_client(project_id)
    table_ref = f"{project_id}.{dataset_id}.{table_id}"

    job_config = bigquery.LoadJobConfig(
        write_disposition=write_disposition,
        autodetect=True,
    )

    load_job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    load_job.result()  # Wait for completion
