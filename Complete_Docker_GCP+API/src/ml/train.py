from __future__ import annotations

from dataclasses import asdict, dataclass
import joblib
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score


@dataclass
class Metrics:
    mse: float
    rmse: float
    r2: float


def train_and_evaluate(X, y, test_size: float = 0.2, random_state: int = 42):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    # Simple baseline model for tabular data
    model = RandomForestRegressor(
        n_estimators=300,
        random_state=random_state,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)

    mse = float(mean_squared_error(y_test, preds))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y_test, preds))

    return model, asdict(Metrics(mse=mse, rmse=rmse, r2=r2))


def save_model(model, path: str) -> None:
    joblib.dump(model, path)
