"""Data pipeline utilities for the house price workshop.

This module handles synthetic dataset creation, missing value injection,
raw data saving, cleaning, and reading the processed dataset back.
"""

import numpy as np
import pandas as pd
from config import RAW_DATA_FILE, PROCESSED_DATA_FILE, RAW_DIR, PROCESSED_DIR


def create_data_dirs():
    """Create the raw and processed data directories if they do not exist."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def generate_synthetic_data(rows: int = 150, random_seed: int = 42) -> pd.DataFrame:
    """Build a synthetic housing dataset with numeric and categorical features."""
    np.random.seed(random_seed)
    data = {
        "area": np.random.randint(500, 3500, rows),
        "bedrooms": np.random.randint(1, 5, rows),
        "bathrooms": np.random.randint(1, 4, rows),
        "location": np.random.choice(["Urban", "Suburban", "Rural"], rows),
    }
    df = pd.DataFrame(data)
    df["price"] = (
        df["area"] * 300
        + df["bedrooms"] * 50000
        + df["bathrooms"] * 30000
        + df["location"].map({"Urban": 200000, "Suburban": 100000, "Rural": 50000})
        + np.random.randint(10000, 50000, rows)
    )
    return df


def save_raw_data(df: pd.DataFrame):
    """Save generated raw data as an Excel workbook."""
    create_data_dirs()
    df.to_excel(RAW_DATA_FILE, index=False, engine="openpyxl")
    return RAW_DATA_FILE


def load_raw_data() -> pd.DataFrame:
    """Load the raw Excel dataset from disk."""
    create_data_dirs()
    return pd.read_excel(RAW_DATA_FILE, engine="openpyxl")


def fill_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing numeric and categorical values using simple rules."""
    df = df.copy()
    numeric_cols = ["area", "bedrooms", "bathrooms"]
    for col in numeric_cols:
        median = df[col].median()
        df[col] = df[col].fillna(median)

    if "location" in df.columns:
        mode_loc = df["location"].mode()
        fill_value = mode_loc[0] if len(mode_loc) > 0 else "Urban"
        df["location"] = df["location"].fillna(fill_value)

    df["price"] = df["price"].fillna(df["price"].median())
    return df


def introduce_missing_values(df: pd.DataFrame, fraction: float = 0.1) -> pd.DataFrame:
    """Introduce synthetic missing values to raw data for cleaning demonstration."""
    df = df.copy()
    nrows = len(df)
    for col in ["area", "bedrooms", "bathrooms"]:
        missing_count = max(1, int(nrows * fraction))
        missing_idx = np.random.choice(df.index, missing_count, replace=False)
        df.loc[missing_idx, col] = np.nan

    missing_loc_count = max(1, int(nrows * (fraction / 2)))
    missing_loc_idx = np.random.choice(df.index, missing_loc_count, replace=False)
    df.loc[missing_loc_idx, "location"] = np.nan
    return df


def prepare_processed_data(df: pd.DataFrame):
    """Save cleaned data to the processed dataset path."""
    create_data_dirs()
    df.to_excel(PROCESSED_DATA_FILE, index=False, engine="openpyxl")
    return PROCESSED_DATA_FILE


def generate_and_save_raw(rows: int = 150, random_seed: int = 42):
    """Create raw synthetic data and store it in the raw data folder."""
    df = generate_synthetic_data(rows=rows, random_seed=random_seed)
    df = introduce_missing_values(df)
    save_raw_data(df)
    return RAW_DATA_FILE


def clean_raw_data():
    """Load raw data, fill missing values, and save the cleaned dataset."""
    df = load_raw_data()
    cleaned_df = fill_missing_values(df)
    prepare_processed_data(cleaned_df)
    return PROCESSED_DATA_FILE


def run_data_pipeline() -> pd.DataFrame:
    """Run the raw generation and cleaning pipeline, then return processed data."""
    generate_and_save_raw()
    clean_raw_data()
    return load_processed_data()


def load_processed_data() -> pd.DataFrame:
    """Load the cleaned training dataset from disk."""
    create_data_dirs()
    return pd.read_excel(PROCESSED_DATA_FILE, engine="openpyxl")
