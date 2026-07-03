"""Model quality gate used by the CI/CD pipeline.

Reads the metadata written by the most recent `train.py` run and fails
(non-zero exit) if the model does not meet the minimum quality bar. This is
the stage that stops a bad model from being packaged and deployed.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import MODEL_INFO  # noqa: E402

MIN_R2 = 0.85


def main() -> int:
    if not MODEL_INFO.exists():
        print(f"No model metadata found at {MODEL_INFO}. Run training first.")
        return 1

    with open(MODEL_INFO, "r", encoding="utf-8") as f:
        info = json.load(f)

    r2 = info.get("r2")
    if r2 is None:
        print("Model metadata is missing an 'r2' value.")
        return 1

    print(f"run_id={info.get('run_id')} rmse={info.get('rmse'):.2f} mae={info.get('mae'):.2f} r2={r2:.4f}")

    if r2 < MIN_R2:
        print(f"FAIL: r2 {r2:.4f} is below the required minimum of {MIN_R2}")
        return 1

    print(f"PASS: r2 {r2:.4f} meets the required minimum of {MIN_R2}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
