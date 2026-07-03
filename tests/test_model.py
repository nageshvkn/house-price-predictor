import pandas as pd

from model import (
    transform_features,
    prepare_training_data,
    train_model,
    evaluate_model,
    predict_from_input,
    LOCATION_FEATURES,
)


def _sample_df():
    return pd.DataFrame(
        {
            "area": [1000, 1500, 2000, 2500],
            "bedrooms": [2, 3, 3, 4],
            "bathrooms": [1, 2, 2, 3],
            "location": ["Urban", "Suburban", "Rural", "Urban"],
            "price": [250000, 350000, 300000, 500000],
        }
    )


def test_transform_features_has_expected_columns():
    features = transform_features(_sample_df())
    expected = ["area", "bedrooms", "bathrooms"] + LOCATION_FEATURES
    assert list(features.columns) == expected
    assert features.shape[0] == 4


def test_transform_features_requires_location_column():
    df = _sample_df().drop(columns=["location"])
    try:
        transform_features(df)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_train_and_evaluate_model_returns_metrics():
    df = _sample_df()
    X, y = prepare_training_data(df)
    model = train_model(X, y)
    metrics = evaluate_model(model, X, y)
    assert set(metrics.keys()) == {"rmse", "mae", "r2"}
    assert metrics["rmse"] >= 0
    assert metrics["mae"] >= 0


def test_predict_from_input_returns_float():
    df = _sample_df()
    X, y = prepare_training_data(df)
    model = train_model(X, y)
    prediction = predict_from_input(model, area=1800, bedrooms=3, bathrooms=2, location="Urban")
    assert isinstance(prediction, float)
