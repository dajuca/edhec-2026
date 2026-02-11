from __future__ import annotations

import pandas as pd
import numpy as np


NUM_COLS = ["price", "price_before", "price_difference", "price_percent_change"]
CAT_COLS = ["brand", "currency", "collection", "life_span"]


def clean_and_prepare(df: pd.DataFrame):
    """
    - Basic cleaning
    - Feature engineering:
      - parse life_span_date
      - simple numeric imputation
      - one-hot for categorical
      - standardization for numeric features
    - Target: price
    Returns:
      df_clean, X, y, feature_names
    """
    df = df.copy()

    # Ensure numeric
    for c in NUM_COLS:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # Parse dates (optional: can be used as feature)
    if "life_span_date" in df.columns:
        df["life_span_date"] = pd.to_datetime(df["life_span_date"], errors="coerce")
        df["life_span_year"] = df["life_span_date"].dt.year
        df["life_span_month"] = df["life_span_date"].dt.month
    else:
        df["life_span_year"] = np.nan
        df["life_span_month"] = np.nan

    # Drop rows without target
    df = df.dropna(subset=["price"])

    # Fill numeric missing with median
    for c in ["price_before", "price_difference", "price_percent_change", "life_span_year", "life_span_month"]:
        if c in df.columns:
            df[c] = df[c].fillna(df[c].median())

    # Fill categorical missing
    for c in CAT_COLS:
        if c in df.columns:
            df[c] = df[c].fillna("UNKNOWN").astype(str)

    # Build features
    feature_num = ["price_before", "price_difference", "price_percent_change", "life_span_year", "life_span_month"]
    feature_num = [c for c in feature_num if c in df.columns]

    X_num = df[feature_num].astype(float)

    # Standardize numeric (z-score)
    X_num = (X_num - X_num.mean()) / (X_num.std(ddof=0) + 1e-9)

    # One-hot encode categorical
    X_cat = pd.get_dummies(df[[c for c in CAT_COLS if c in df.columns]], drop_first=False)

    X = pd.concat([X_num, X_cat], axis=1)
    y = df["price"].astype(float)

    feature_names = list(X.columns)

    # cleaned data to upload (keep useful cols + engineered)
    keep_cols = [c for c in df.columns if c not in []]
    df_clean = df[keep_cols].copy()

    return df_clean, X, y, feature_names
