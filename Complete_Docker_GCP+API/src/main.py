import os
from datetime import datetime

import pandas as pd

from src.bq.query import fetch_prices
from src.bq.upload import create_dataset, upload_dataframe
from src.fx.exchange_rates import fetch_exchange_rates
from src.ml.preprocess import clean_and_prepare
from src.ml.train import train_and_evaluate, save_model


def env(name: str, default: str | None = None) -> str:
    v = os.getenv(name, default)
    if v is None or v == "":
        raise ValueError(f"Missing required env var: {name}")
    return v


def main() -> None:
    project_id = env("GCP_PROJECT_ID", "edhec-01")
    source_dataset_id = env("SOURCE_DATASET_ID", "luxurydata2502")
    source_table_id = env("SOURCE_TABLE_ID", "price-monitoring-2022")
    brand = env("BRAND", "Cartier")
    location = env("BQ_LOCATION", "EU")
    fx_api_url = env("FX_API_URL")

    print("=== 1) Fetching data from BigQuery ===")
    df_raw = fetch_prices(
        project_id=project_id,
        dataset_id=source_dataset_id,
        table_id=source_table_id,
        brand=brand,
        limit=10,
    )
    print(df_raw.head())
    print(f"Rows: {len(df_raw)}")

    print("=== 2) Cleaning + feature engineering ===")
    df_clean, X, y, feature_names = clean_and_prepare(df_raw)
    print(df_clean.head())
    print(f"Features: {len(feature_names)}")

    print("=== 3) Train ML model (predict price) ===")
    model, metrics = train_and_evaluate(X, y)
    print("Metrics:", metrics)

    model_path = "/app/models/model.joblib"
    save_model(model, model_path)
    print(f"Saved model to {model_path}")

    print("=== 4) Create a new dataset and upload cleaned data ===")
    run_suffix = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    target_dataset_id = f"luxury_cleaned_{run_suffix}"

    create_dataset(project_id=project_id, dataset_id=target_dataset_id, location=location)

    # Upload cleaned prices
    upload_dataframe(
        project_id=project_id,
        dataset_id=target_dataset_id,
        table_id="cleaned_prices",
        df=df_clean,
        write_disposition="WRITE_TRUNCATE",
    )
    print(f"Uploaded cleaned_prices to {project_id}.{target_dataset_id}.cleaned_prices")

    print("=== 5) Fetch FX rates and upload to BigQuery ===")
    df_fx = fetch_exchange_rates(fx_api_url)
    upload_dataframe(
        project_id=project_id,
        dataset_id=target_dataset_id,
        table_id="fx_rates_eur",
        df=df_fx,
        write_disposition="WRITE_TRUNCATE",
    )
    print(f"Uploaded fx_rates_eur to {project_id}.{target_dataset_id}.fx_rates_eur")

    print("=== DONE ✅ ===")


if __name__ == "__main__":
    main()
