from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any
import pandas as pd


@dataclass
class PipelineState:
    # Raw from BigQuery
    raw_df: Optional[pd.DataFrame] = None
    # Cleaned df uploaded to BigQuery
    cleaned_df: Optional[pd.DataFrame] = None
    # FX rates df uploaded to BigQuery
    fx_df: Optional[pd.DataFrame] = None
    # ML feature matrix and metadata
    feature_names: Optional[list[str]] = None
    # Metrics dict
    metrics: Optional[Dict[str, Any]] = None
    # Trained model
    model: Any = None
    # Last run info
    last_run_utc: Optional[str] = None
    target_dataset_id: Optional[str] = None


STATE = PipelineState()
