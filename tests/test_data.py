import numpy as np
import pandas as pd

from data import (
    generate_synthetic_data,
    introduce_missing_values,
    fill_missing_values,
)


def test_generate_synthetic_data_shape_and_columns():
    df = generate_synthetic_data(rows=50, random_seed=1)
    assert len(df) == 50
    assert list(df.columns) == ["area", "bedrooms", "bathrooms", "location", "price"]
    assert df["location"].isin(["Urban", "Suburban", "Rural"]).all()


def test_introduce_missing_values_adds_nans():
    df = generate_synthetic_data(rows=100, random_seed=1)
    dirty = introduce_missing_values(df, fraction=0.2)
    assert dirty["area"].isna().sum() > 0
    assert dirty["bedrooms"].isna().sum() > 0
    assert dirty["location"].isna().sum() > 0
    # original frame must stay untouched
    assert df["area"].isna().sum() == 0


def test_fill_missing_values_removes_all_nans():
    df = pd.DataFrame(
        {
            "area": [1000.0, np.nan, 2000.0],
            "bedrooms": [2, 3, np.nan],
            "bathrooms": [1, np.nan, 2],
            "location": ["Urban", None, "Rural"],
            "price": [100000.0, np.nan, 300000.0],
        }
    )
    cleaned = fill_missing_values(df)
    assert cleaned.isna().sum().sum() == 0
    assert cleaned["location"].iloc[1] in {"Urban", "Rural"}
