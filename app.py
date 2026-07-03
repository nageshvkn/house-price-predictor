"""Flask web app for the workshop demo.

This module loads the latest trained model and metadata, serves the prediction UI,
provides a simple `/status` health endpoint, and renders the experiment dashboard.
"""

import os
import pickle
import json
import socket

from flask import Flask, render_template, request, jsonify
import pandas as pd

from config import EXPERIMENT_LOG, MODEL_INFO, MODEL_REGISTRY
from model import predict_from_input

app = Flask(__name__)

# Load the latest model artifact and model metadata if available.
model = None
model_info = {}

try:
    with open(MODEL_REGISTRY, "rb") as f:
        model = pickle.load(f)
except FileNotFoundError:
    model = None

try:
    with open(MODEL_INFO, "r", encoding="utf-8") as f:
        model_info = json.load(f)
except FileNotFoundError:
    model_info = {}


@app.route("/home")
def home_page():
    """Render the landing home page."""
    return render_template("home.html")


@app.route("/")
def home():
    """Render the main prediction page with model metadata."""
    return render_template("index.html", model_info=model_info)


@app.route("/status")
def status():
    """Return current model status and metadata as JSON."""
    if not model_info:
        return jsonify({"status": "no_model", "message": "No trained model found. Run train.py first."})
    return jsonify(model_info)


@app.route("/predict", methods=["POST"])
def predict():
    """Accept user input, run prediction, and return JSON response."""
    if model is None:
        return jsonify({"error": "Model not available. Run train.py first."}), 503

    area = float(request.form.get("area", 0))
    bedrooms = int(request.form.get("bedrooms", 0))
    bathrooms = int(request.form.get("bathrooms", 0))
    location = request.form.get("location", "Urban")

    prediction = predict_from_input(model, area, bedrooms, bathrooms, location)
    return jsonify(
        {
            "price": round(prediction, 2),
            "version": model_info.get("run_id", "unknown"),
            "rmse": model_info.get("rmse"),
            "mae": model_info.get("mae"),
            "r2": model_info.get("r2"),
        }
    )


def load_experiment_log():
    """Read experiment history from CSV and normalize it for the dashboard."""
    if not EXPERIMENT_LOG.exists():
        return []

    df = pd.read_csv(EXPERIMENT_LOG, parse_dates=["timestamp"])
    df = df.sort_values("timestamp")
    df["rmse"] = pd.to_numeric(df["rmse"], errors="coerce")
    df["mae"] = pd.to_numeric(df["mae"], errors="coerce")
    df["r2"] = pd.to_numeric(df["r2"], errors="coerce")
    df["rows"] = pd.to_numeric(df["rows"], errors="coerce")
    df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    return df.to_dict(orient="records")


@app.route("/experiments")
def experiments():
    """Render the experiment dashboard with historical run data."""
    experiment_rows = load_experiment_log()
    return render_template("experiments.html", experiments=experiment_rows)


def get_server_port(default_port: int = 5000) -> int:
    """Choose a port for the Flask app, with fallback if the default port is busy."""
    try:
        return int(os.environ.get("PORT", default_port))
    except ValueError:
        return default_port


def find_available_port(start_port: int = 5000, max_tries: int = 10) -> int:
    """Probe for a free port starting from the requested port."""
    for port in range(start_port, start_port + max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"No available port found in range {start_port}-{start_port + max_tries - 1}")


if __name__ == "__main__":
    default_port = get_server_port()
    port = find_available_port(default_port)
    if port != default_port:
        print(f"Port {default_port} is in use. Starting Flask on port {port} instead.")
    app.run(host="0.0.0.0", debug=True, port=port, use_reloader=False)
