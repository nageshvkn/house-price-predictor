"""Command-line entrypoint for the training pipeline.

This script supports staged execution for workshop teaching:
- generate-raw: create raw synthetic data with missing values
- clean-data: clean the raw dataset and save processed output
- train: train the model and log experiment metadata
- full: run the complete pipeline from raw generation to trained model
"""

import argparse
import json
import pickle
from datetime import datetime, timezone
from pathlib import Path

from sklearn.model_selection import train_test_split

from data import generate_and_save_raw, clean_raw_data, load_processed_data
from experiment_tracker import log_experiment
from model import prepare_training_data, train_model, evaluate_model
from config import MODEL_DIR, MODEL_REGISTRY, MODEL_INFO


def create_model_dirs():
    """Ensure the model directory exists before saving artifacts."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)


def save_model(model, path: Path):
    """Serialize a trained model to disk."""
    with open(path, "wb") as f:
        pickle.dump(model, f)


def save_model_info(run_id: str, model_path: Path, metrics: dict, rows: int):
    """Persist metadata about the current training run."""
    info = {
        "run_id": run_id,
        "model_path": str(model_path),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rows": rows,
        **metrics,
    }
    with open(MODEL_INFO, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2)
    return info


def run_full_pipeline(notes: str = "Full workshop pipeline run"):
    """Run the full data generation, cleaning, training, and logging pipeline."""
    print("➡️ Generating raw synthetic data with missing values...")
    raw_path = generate_and_save_raw()
    print(f"   Raw data saved to: {raw_path}")

    print("➡️ Cleaning raw data and writing processed dataset...")
    processed_path = clean_raw_data()
    print(f"   Processed data saved to: {processed_path}")

    return run_training(notes=notes)


def run_training(notes: str = "Manual training run"):
    """Load processed data, train the model, evaluate it, and save training outputs."""
    create_model_dirs()

    df = load_processed_data()
    print(f"➡️ Loaded processed dataset with {len(df)} rows.")

    X, y = prepare_training_data(df)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

    print("➡️ Training the model...")
    model = train_model(X_train, y_train)

    print("➡️ Evaluating the model...")
    metrics = evaluate_model(model, X_test, y_test)
    print(f"   RMSE: {metrics['rmse']:.2f}, MAE: {metrics['mae']:.2f}, R2: {metrics['r2']:.3f}")

    run_id = datetime.now(timezone.utc).strftime("run_%Y%m%d%H%M%S")
    artifact_name = f"model_{run_id}.pkl"
    artifact_path = MODEL_DIR / artifact_name

    save_model(model, artifact_path)
    save_model(model, MODEL_REGISTRY)
    model_info = save_model_info(run_id, artifact_path, metrics, len(df))

    log_experiment(run_id, rows=len(df), model_path=artifact_path, metrics=metrics, notes=notes)

    print("✅ Training complete")
    print(f"   Saved versioned model: {artifact_path.name}")
    print(f"   Latest model registry: {MODEL_REGISTRY.name}")
    print(f"   Experiment log: {MODEL_INFO.name}")
    print(json.dumps(model_info, indent=2))

    return model_info


def generate_raw_data():
    """Generate a raw dataset with missing values and save it for inspection."""
    raw_path = generate_and_save_raw()
    print(f"✅ Raw data generated: {raw_path}")
    print("You can inspect the file and then run `python3 train.py clean-data`.")


def clean_data():
    """Clean existing raw data and write a processed dataset to disk."""
    processed_path = clean_raw_data()
    print(f"✅ Raw data cleaned: {processed_path}")
    print("You can inspect the processed dataset and then run `python3 train.py train`.")


def make_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for staged workshop commands."""
    parser = argparse.ArgumentParser(description="Workshop training pipeline commands")
    subparsers = parser.add_subparsers(dest="command", required=False)

    subparsers.add_parser("generate-raw", help="Generate raw synthetic data with missing values")
    subparsers.add_parser("clean-data", help="Clean raw data and save processed dataset")
    train_parser = subparsers.add_parser("train", help="Train the model using processed data")
    train_parser.add_argument("--notes", default="Manual training run", help="Experiment notes")
    subparsers.add_parser("full", help="Run the full pipeline from data generation to model training")

    return parser


def main():
    """Dispatch CLI commands to the appropriate pipeline stage."""
    parser = make_parser()
    args = parser.parse_args()

    if args.command == "generate-raw":
        generate_raw_data()
    elif args.command == "clean-data":
        clean_data()
    elif args.command == "train":
        run_training(notes=args.notes)
    else:
        run_full_pipeline()


if __name__ == "__main__":
    main()
