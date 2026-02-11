from __future__ import annotations

import os
from datetime import datetime
from typing import Optional, Dict, Any

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from src.api_state import STATE
from src.bq.query import fetch_prices
from src.bq.upload import create_dataset, upload_dataframe
from src.fx.exchange_rates import fetch_exchange_rates
from src.ml.preprocess import clean_and_prepare
from src.ml.train import train_and_evaluate, save_model


app = FastAPI(title="Luxury BigQuery + ML API", version="1.0.0")

# Power BI Desktop typically doesn't require CORS, but enabling it makes browser testing easier
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def env(name: str, default: Optional[str] = None) -> str:
    v = os.getenv(name, default)
    if v is None or v == "":
        raise ValueError(f"Missing required env var: {name}")
    return v


def df_to_records(df: pd.DataFrame, limit: int = 5000):
    if df is None:
        return None
    # Convert NaT to None for JSON
    df2 = df.copy()
    for c in df2.columns:
        if pd.api.types.is_datetime64_any_dtype(df2[c]):
            df2[c] = df2[c].astype("datetime64[ns]")
            df2[c] = df2[c].dt.strftime("%Y-%m-%dT%H:%M:%S")
    return df2.head(limit).to_dict(orient="records")


def run_pipeline(limit: int = 10) -> Dict[str, Any]:
    project_id = env("GCP_PROJECT_ID", "edhec-01")
    source_dataset_id = env("SOURCE_DATASET_ID", "luxurydata2502")
    source_table_id = env("SOURCE_TABLE_ID", "price-monitoring-2022")
    brand = env("BRAND", "Cartier")
    location = env("BQ_LOCATION", "EU")
    fx_api_url = env("FX_API_URL")

    # 1) Fetch
    df_raw = fetch_prices(
        project_id=project_id,
        dataset_id=source_dataset_id,
        table_id=source_table_id,
        brand=brand,
        limit=limit,
    )

    # 2) Clean/prepare
    df_clean, X, y, feature_names = clean_and_prepare(df_raw)

    # 3) Train
    model, metrics = train_and_evaluate(X, y)

    # Save model
    model_path = "/app/models/model.joblib"
    save_model(model, model_path)

    # 4) Upload to a NEW dataset every run
    run_suffix = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    target_dataset_id = f"luxury_cleaned_{run_suffix}"
    create_dataset(project_id=project_id, dataset_id=target_dataset_id, location=location)

    upload_dataframe(
        project_id=project_id,
        dataset_id=target_dataset_id,
        table_id="cleaned_prices",
        df=df_clean,
        write_disposition="WRITE_TRUNCATE",
    )

    # 5) FX rates
    df_fx = fetch_exchange_rates(fx_api_url)
    upload_dataframe(
        project_id=project_id,
        dataset_id=target_dataset_id,
        table_id="fx_rates_eur",
        df=df_fx,
        write_disposition="WRITE_TRUNCATE",
    )

    # Update global state for API consumption
    STATE.raw_df = df_raw
    STATE.cleaned_df = df_clean
    STATE.fx_df = df_fx
    STATE.feature_names = feature_names
    STATE.metrics = metrics
    STATE.model = model
    STATE.last_run_utc = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    STATE.target_dataset_id = target_dataset_id

    return {
        "status": "ok",
        "brand": brand,
        "rows_raw": int(len(df_raw)),
        "rows_cleaned": int(len(df_clean)),
        "metrics": metrics,
        "target_dataset_id": target_dataset_id,
        "last_run_utc": STATE.last_run_utc,
        "model_path": model_path,
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "last_run_utc": STATE.last_run_utc,
        "target_dataset_id": STATE.target_dataset_id,
    }


@app.post("/run")
def run(limit: int = Query(10, ge=1, le=200000)):
    """Run the whole pipeline (BQ fetch → clean → train → upload → fx upload)"""
    try:
        return run_pipeline(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/prices/raw")
def prices_raw(limit: int = Query(1000, ge=1, le=5000)):
    if STATE.raw_df is None:
        raise HTTPException(status_code=400, detail="No data loaded. Call POST /run first.")
    return {"rows": df_to_records(STATE.raw_df, limit=limit)}


@app.get("/prices/cleaned")
def prices_cleaned(limit: int = Query(1000, ge=1, le=5000)):
    if STATE.cleaned_df is None:
        raise HTTPException(status_code=400, detail="No data loaded. Call POST /run first.")
    return {"rows": df_to_records(STATE.cleaned_df, limit=limit)}


@app.get("/fx")
def fx_rates(limit: int = Query(5000, ge=1, le=5000)):
    if STATE.fx_df is None:
        raise HTTPException(status_code=400, detail="No FX data loaded. Call POST /run first.")
    return {"rows": df_to_records(STATE.fx_df, limit=limit)}


@app.get("/ml/metrics")
def ml_metrics():
    if STATE.metrics is None:
        raise HTTPException(status_code=400, detail="No metrics available. Call POST /run first.")
    return {"metrics": STATE.metrics, "feature_count": len(STATE.feature_names or [])}


@app.get("/ml/predict")
def ml_predict(
    price_before: float = Query(...),
    price_difference: float = Query(...),
    price_percent_change: float = Query(...),
    life_span_year: int = Query(...),
    life_span_month: int = Query(...),
    brand: str = Query("Cartier"),
    currency: str = Query("EUR"),
    collection: str = Query("UNKNOWN"),
    life_span: str = Query("UNKNOWN"),
):
    """
    Predict price for a hypothetical item.
    Note: features must match the training preprocessing; categorical values unseen at train time may be ignored.
    """
    if STATE.model is None or STATE.feature_names is None:
        raise HTTPException(status_code=400, detail="No model loaded. Call POST /run first.")

    # Build a single-row dataframe shaped like the training columns
    row = {
        "price_before": price_before,
        "price_difference": price_difference,
        "price_percent_change": price_percent_change,
        "life_span_year": life_span_year,
        "life_span_month": life_span_month,
        "brand": brand,
        "currency": currency,
        "collection": collection,
        "life_span": life_span,
    }
    df = pd.DataFrame([row])

    # Apply the same preprocessing logic in a minimal way (mirror src/ml/preprocess.py)
    # Numeric standardization: we can't replicate training mean/std without persisting them.
    # For a teaching repo, we use a pragmatic approach:
    # - Build dummies for categorical
    # - Keep numeric as-is (model will still run; accuracy depends on training)
    num_cols = ["price_before", "price_difference", "price_percent_change", "life_span_year", "life_span_month"]
    X_num = df[num_cols].astype(float)

    X_cat = pd.get_dummies(df[["brand", "currency", "collection", "life_span"]], drop_first=False)

    X = pd.concat([X_num, X_cat], axis=1)

    # Align to training feature space
    for col in STATE.feature_names:
        if col not in X.columns:
            X[col] = 0.0
    X = X[STATE.feature_names]

    pred = float(STATE.model.predict(X)[0])
    return {"predicted_price": pred, "input": row}
