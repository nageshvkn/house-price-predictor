"""Experiment tracking utilities for the workshop demo.

This module writes experiment metadata into a CSV file and provides a helper to
read the most recent run.
"""

import csv
from pathlib import Path
from datetime import datetime
from config import EXPERIMENT_DIR, EXPERIMENT_LOG


def create_experiment_dirs():
    """Ensure the experiment directory exists before logging runs."""
    EXPERIMENT_DIR.mkdir(parents=True, exist_ok=True)


def log_experiment(run_id: str, rows: int, model_path: Path, metrics: dict, notes: str = ""):
    """Append a new training experiment row to the CSV log."""
    create_experiment_dirs()
    fieldnames = ["run_id", "timestamp", "rows", "model_path", "rmse", "mae", "r2", "notes"]
    is_new = not EXPERIMENT_LOG.exists()
    with open(EXPERIMENT_LOG, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if is_new:
            writer.writeheader()
        writer.writerow(
            {
                "run_id": run_id,
                "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
                "rows": rows,
                "model_path": str(model_path),
                "rmse": metrics.get("rmse", ""),
                "mae": metrics.get("mae", ""),
                "r2": metrics.get("r2", ""),
                "notes": notes,
            }
        )


def load_last_experiment():
    """Return the most recent experiment row from the log, or None if missing."""
    if not EXPERIMENT_LOG.exists():
        return None
    with open(EXPERIMENT_LOG, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
        return reader[-1] if reader else None
