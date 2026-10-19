"""Command-line entrypoint for the training pipeline.

This script supports staged execution for workshop teaching:
- generate-raw: create raw synthetic data with missing values
- clean-data: clean the raw dataset and save processed output
- train: train the model and log experiment metadata
- full: run the complete pipeline from raw generation to trained model
"""

import argparse
import json
import os
import pickle
from datetime import datetime, timezone
from pathlib import Path

import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split

from data import generate_and_save_raw, clean_raw_data, load_processed_data
from model import prepare_training_data, train_model, evaluate_model
from config import METRICS_FILE, MODEL_DIR, MODEL_REGISTRY, MODEL_INFO


def create_model_dirs():
    """Ensure the model directory exists before saving artifacts."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)


def save_model(model, path: Path):
    """Serialize a trained model to disk."""
    with open(path, "wb") as f:
        pickle.dump(model, f)


def save_model_info(run_id: str, metrics: dict, rows: int):
    """Persist metadata about the current training run."""
    info = {
        "run_id": run_id,
        "model_path": str(MODEL_REGISTRY.relative_to(MODEL_DIR.parent)),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rows": rows,
        **metrics,
    }
    with open(MODEL_INFO, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2)
    return info


def run_training(test_size: float = 0.25, random_seed: int = 42):
    """Train on the processed dataset and log the run and model to MLflow."""
    create_model_dirs()

    df = load_processed_data()
    print(f"➡️ Loaded processed dataset with {len(df)} rows.")

    X, y = prepare_training_data(df)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_seed
    )

    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment("house-price-predictor")

    with mlflow.start_run(run_name="linear-regression") as run:
        print("➡️ Training the model...")
        model = train_model(X_train, y_train)

        print("➡️ Evaluating the model...")
        metrics = evaluate_model(model, X_test, y_test)
        print(
            f"   RMSE: {metrics['rmse']:.2f}, MAE: {metrics['mae']:.2f}, "
            f"R2: {metrics['r2']:.3f}"
        )

        mlflow.log_params(
            {
                "algorithm": "LinearRegression",
                "rows": len(df),
                "test_size": test_size,
                "random_seed": random_seed,
            }
        )
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(model, name="model")

        run_id = run.info.run_id
        save_model(model, MODEL_REGISTRY)
        model_info = save_model_info(run_id, metrics, len(df))
        with open(METRICS_FILE, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)
        print(f"   MLflow run: {run_id}")
        print(f"   Model registry: {MODEL_REGISTRY.name}")

    print("✅ Training complete")
    print(json.dumps(model_info, indent=2))
    return model_info


def make_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for staged workshop commands."""
    parser = argparse.ArgumentParser(description="Workshop training pipeline commands")
    subparsers = parser.add_subparsers(dest="command", required=False)

    raw_parser = subparsers.add_parser(
        "generate-raw", help="Generate raw synthetic data with missing values"
    )
    raw_parser.add_argument("--rows", type=int, default=150)
    raw_parser.add_argument("--seed", type=int, default=42)
    subparsers.add_parser("clean-data", help="Clean raw data and save processed dataset")
    train_parser = subparsers.add_parser("train", help="Train the model using processed data")
    train_parser.add_argument("--test-size", type=float, default=0.25)
    train_parser.add_argument("--seed", type=int, default=42)

    return parser


def main():
    """Dispatch CLI commands to the appropriate pipeline stage."""
    parser = make_parser()
    args = parser.parse_args()

    if args.command == "generate-raw":
        generate_and_save_raw(rows=args.rows, random_seed=args.seed)
    elif args.command == "clean-data":
        clean_raw_data()
    elif args.command == "train":
        run_training(test_size=args.test_size, random_seed=args.seed)
    else:
        parser.error("Choose a pipeline stage; run the complete workflow with `dvc repro`.")


if __name__ == "__main__":
    main()
