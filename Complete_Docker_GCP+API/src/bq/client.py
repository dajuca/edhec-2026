from google.cloud import bigquery


def get_bq_client(project_id: str) -> bigquery.Client:
    # GOOGLE_APPLICATION_CREDENTIALS should be set to the mounted JSON path
    return bigquery.Client(project=project_id)
