import app as app_module


def test_predict_endpoint_returns_prediction_and_model_metrics(monkeypatch):
    monkeypatch.setattr(app_module, "model", object())
    monkeypatch.setattr(
        app_module,
        "model_info",
        {"run_id": "sample-run", "rmse": 1200.0, "mae": 900.0, "r2": 0.91},
    )
    monkeypatch.setattr(app_module, "predict_from_input", lambda *args: 250000.126)

    response = app_module.app.test_client().post(
        "/predict",
        data={
            "area": "1800",
            "bedrooms": "3",
            "bathrooms": "2",
            "location": "Urban",
        },
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "price": 250000.13,
        "version": "sample-run",
        "rmse": 1200.0,
        "mae": 900.0,
        "r2": 0.91,
    }


def test_predict_endpoint_rejects_invalid_input(monkeypatch):
    monkeypatch.setattr(app_module, "model", object())

    response = app_module.app.test_client().post(
        "/predict",
        data={"area": "not-a-number", "bedrooms": "3", "bathrooms": "2", "location": "Urban"},
    )

    assert response.status_code == 400
    assert "error" in response.get_json()
