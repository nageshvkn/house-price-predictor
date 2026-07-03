from pathlib import Path

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
MODEL_DIR = ROOT / "models"
EXPERIMENT_DIR = ROOT / "experiments"
MODEL_REGISTRY = MODEL_DIR / "latest_model.pkl"
MODEL_INFO = MODEL_DIR / "latest_model_info.json"
EXPERIMENT_LOG = EXPERIMENT_DIR / "experiment_log.csv"
RAW_DATA_FILE = RAW_DIR / "house_prices_raw_v1.xlsx"
PROCESSED_DATA_FILE = PROCESSED_DIR / "house_prices_train.xlsx"
