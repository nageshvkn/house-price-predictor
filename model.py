"""Model training and inference helpers for the house price predictor.

This module handles feature encoding, model fitting, prediction generation, and basic
evaluation metrics for model quality reporting.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

# Expected dummy-encoded location features for the regression model.
LOCATION_FEATURES = ["location_Suburban", "location_Urban"]


def _ensure_location_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Guarantee that all expected location dummy columns are present."""
    for name in LOCATION_FEATURES:
        if name not in df.columns:
            df[name] = 0
    return df[LOCATION_FEATURES]


def transform_features(df: pd.DataFrame) -> pd.DataFrame:
    """Convert raw input data into the numeric features expected by the model."""
    df = df.copy()
    if "location" not in df.columns:
        raise ValueError("Input data must contain a 'location' column.")

    encoded = pd.get_dummies(df["location"], prefix="location", drop_first=True)
    encoded = _ensure_location_columns(encoded)
    numeric = df[["area", "bedrooms", "bathrooms"]].astype(float)
    return pd.concat([numeric, encoded], axis=1)


def prepare_training_data(df: pd.DataFrame):
    """Build training input (X) and target (y) arrays from the cleaned dataset."""
    X = transform_features(df)
    y = df["price"].astype(float)
    return X, y


def train_model(X: pd.DataFrame, y: pd.Series):
    """Train a simple linear regression model on the prepared training data."""
    model = LinearRegression()
    model.fit(X, y)
    return model


def predict_from_input(model, area, bedrooms, bathrooms, location):
    """Create a single sample from user input and return the model prediction."""
    sample = pd.DataFrame(
        [
            {
                "area": float(area),
                "bedrooms": float(bedrooms),
                "bathrooms": float(bathrooms),
                "location": location,
            }
        ]
    )
    features = transform_features(sample)
    return float(model.predict(features)[0])


def evaluate_model(model, X, y):
    """Evaluate the trained model and return RMSE, MAE, and R2 metrics."""
    predictions = model.predict(X)
    residuals = y - predictions
    rmse = np.sqrt(np.mean(residuals ** 2))
    mae = np.mean(np.abs(residuals))
    ss_total = np.sum((y - np.mean(y)) ** 2)
    ss_residual = np.sum((y - predictions) ** 2)
    r2 = 1 - ss_residual / ss_total if ss_total != 0 else 0.0
    return {
        "rmse": float(rmse),
        "mae": float(mae),
        "r2": float(r2),
    }
