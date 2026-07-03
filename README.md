# House Price Predictor — MLOps Workshop Demo

A simple end-to-end workshop project that demonstrates a lightweight MLOps workflow using a housing price prediction app.

## Why this project works for a workshop

It shows the full path from:
- raw data creation and inspection
- missing-value handling
- model training and evaluation
- experiment tracking
- model versioning
- deployment and inference
- reproducibility

All with minimal code and accessible files.

## Workshop demo flow

### Step 1 — Setup the environment

This is the first step in the workshop, and it should be executed before anything else.

1. Create a fresh Python virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install the required packages:

```bash
pip install -r requirements.txt
```

What to explain:
- `venv` creates an isolated environment so dependencies do not interfere with system Python or other projects.
- The shell prompt will show `(venv)` after activation, confirming the environment is active.
- `requirements.txt` defines the exact dependencies needed to run the app, train the model, and render the dashboard.

Verification:
- Run `python -m pip list` to confirm that Flask, pandas, scikit-learn, openpyxl, and other libraries are installed.

### Step 2 — Inspect the project structure and raw data

Review key project files and directories before running the pipeline:

- `data.py` — synthetic Excel raw data creation, missing-value injection, cleaning, and processed data saving
- `model.py` — feature transformation, model training, prediction, and evaluation helpers
- `train.py` — orchestrates data pipeline, training, evaluation, model storage, and experiment logging
- `experiment_tracker.py` — records training runs in `experiments/experiment_log.csv`
- `app.py` — Flask service that loads the latest model and serves predictions
- `templates/index.html` — interactive browser prediction UI
- `templates/experiments.html` — experiment dashboard with charts
- `config.py` — central path definitions for data, models, and experiments
- `models/` — trained model artifacts and model registry
- `data/raw/` — raw Excel dataset for the data-demo step
- `data/processed/` — cleaned Excel dataset used for training
- `experiments/` — experiment history log

Review the raw dataset:
- Open `data/raw/house_prices_raw_v1.xlsx`.
- Identify the feature columns: `area`, `bedrooms`, `bathrooms`, `location`.
- Identify the target column: `price`.
- Point out missing values and explain why the raw file is not yet ready for machine learning.

### Step 3 — Run the pipeline in stages

This workshop now supports manual execution of each stage.

#### Generate raw synthetic data

```bash
python3 train.py generate-raw
```

What happens:
- synthetic raw data is generated and saved to `data/raw/house_prices_raw_v1.xlsx`
- missing values are introduced to simulate imperfect real data
- the file is ready for inspection before cleaning

What to show:
- open `data/raw/house_prices_raw_v1.xlsx`
- point out missing values and the raw feature/target columns

#### Clean the raw data

```bash
python3 train.py clean-data
```

What happens:
- raw data is loaded from `data/raw/house_prices_raw_v1.xlsx`
- missing values are filled using simple rules
- cleaned data is saved to `data/processed/house_prices_train.xlsx`

What to show:
- open the processed file and compare it with the raw dataset
- emphasize that cleaning is a separate step from training

#### Train the model

```bash
python3 train.py train
```

What happens:
- processed data is loaded from `data/processed/house_prices_train.xlsx`
- the model is trained on a training split
- the model is evaluated on a test split
- metrics are printed: RMSE, MAE, and R2
- a versioned model artifact is written to `models/`
- the run is logged to `experiments/experiment_log.csv`

What to show:
- terminal output with metrics
- created files:
  - `models/latest_model.pkl`
  - `models/latest_model_info.json`
  - `experiments/experiment_log.csv`

Explain:
- `run_id` identifies each experiment uniquely.
- the timestamp records when the run happened.
- metrics like RMSE, MAE, and R2 show model accuracy and fit.

#### Run everything end-to-end

```bash
python3 train.py full
```

What happens:
- raw data is generated
- the data is cleaned
- the model is trained and logged

Use this once you’ve shown the stages individually to demonstrate the full pipeline.

### Step 4 — Open the experiment dashboard

Start the Flask app:

```bash
python3 app.py
```

Open these pages:
- `http://127.0.0.1:5000/`
- `http://127.0.0.1:5000/experiments`

What to show:
- the dashboard summary cards: total runs, best RMSE, best MAE, best R2.
- the chart of metrics across experiment runs.
- the experiment log table with notes.

Explain:
- this dashboard makes experiment history easier to understand than a plain CSV.
- it is useful for comparing model improvements over multiple training runs.

### Step 5 — Use the prediction UI

In the browser at `http://127.0.0.1:5000/`:
- enter values for `area`, `bedrooms`, `bathrooms`, and `location`.
- submit the form and show the predicted price.
- point out that the app uses the latest saved model.

Explain:
- training and serving are separated by design.
- the app provides a simple way to turn a model into a working demo.

### Step 6 — Check experiment metadata

Optional endpoints:
- `http://127.0.0.1:5000/status`
  - returns the latest model metadata as JSON.
- `experiments/experiment_log.csv`
  - can be opened directly if you want the raw values.

Explain:
- the dashboard is built from the same experiment log file.
- the JSON status endpoint is useful for programmatic checks.

### Step 7 — Reset and rerun

To repeat the workshop from scratch, run this single cleanup command from the repo root:

```bash
rm -f models/latest_model.pkl models/latest_model_info.json experiments/experiment_log.csv data/processed/house_prices_train.xlsx
```

Then rerun `python3 train.py` and `python3 app.py`.

Explain:
- this simulates a fresh project run.
- it is useful for workshops when you want to demonstrate the entire flow again.

## Part 2 — CI/CD with Jenkins

This part shows the same pipeline (lint, test, train, validate, package, deploy)
first run manually stage-by-stage, then automated end-to-end by Jenkins.

Files involved:
- `Makefile` — one target per stage (`setup`, `lint`, `test`, `train`, `validate`, `build`, `deploy`, `smoke`). Running these by hand *is* the manual demo.
- `tests/` — unit tests for `data.py` and `model.py`.
- `scripts/validate_model.py` — the model quality gate; fails the pipeline if R2 drops below 0.85.
- `Dockerfile` — packages the Flask app + trained model into a runnable image.
- `Jenkinsfile` — declarative pipeline; each stage just calls the matching `make` target.
- `docker-compose.yml` + `jenkins/Dockerfile` — a self-contained Jenkins instance (with Python, Docker CLI, and Make preinstalled) so the whole demo runs on one laptop.

### Step 8 — Run every stage manually first

Run each command one at a time and explain what it represents before moving to the next:

```bash
make setup     # install deps into .venv -- "this is what CI does before anything else"
make lint      # style/static checks -- "catches issues before they reach a teammate"
make test      # unit tests -- "regression safety net"
make train     # train + evaluate -- "same training step as Part 1, run non-interactively"
make validate  # model quality gate -- "a bad model should never reach deployment"
make build     # docker build -- "package the app + trained model into one artifact"
make deploy    # docker run -- "roll the artifact out, same way every time"
make smoke     # curl the live endpoint -- "prove the deployment actually works"
```

Open `http://localhost:5050/status` to show the live, container-served app after `make deploy`.

To break it on purpose (shows the gate stopping a bad release): temporarily edit
`scripts/validate_model.py` and raise `MIN_R2` above what the model actually
achieves (e.g. `0.99`), run `make validate`, show it fail, then revert.

Reset between demos with `make clean` (mirrors Step 7, plus stops the container: `docker rm -f house-price-app`).

### Step 9 — Same steps, one command

```bash
make pipeline
```

This just chains every target above in order — the bridge concept before
introducing Jenkins: *"Jenkins is going to run exactly this."*

### Step 10 — Stand up Jenkins

```bash
docker compose up -d --build
```

Grab the initial admin password:

```bash
docker compose logs jenkins | grep -A2 "initial setup"
```

Open `http://localhost:8090`, paste the password, install suggested plugins, create an admin user.

### Step 11 — Create the pipeline job

1. **New Item** → name it `house-price-predictor` → type **Pipeline** → OK.
2. Under **Pipeline**, set:
   - Definition: `Pipeline script from SCM`
   - SCM: `Git`
   - Repository URL: this repo's GitHub URL
   - Branch: `*/main`
   - Script Path: `Jenkinsfile`
3. Under **Build Triggers**, check `Poll SCM` and set schedule to `* * * * *` (checks every minute — avoids needing a public webhook for the workshop).
4. Save, then click **Build Now** for the first manual run.

### Step 12 — Live demo: push a change, watch it deploy

1. Open the build's stage view and walk through it — point out it's the exact same stages as Step 8.
2. Make a small change (e.g. edit a comment or notes string), commit, and push. Within a minute the pipeline auto-triggers.
3. **Break it on purpose**: same trick as Step 8 (bump `MIN_R2` in `scripts/validate_model.py` too high), push, and show the `Model Quality Gate` stage fail red — deployment never runs, the previous container keeps serving traffic untouched.
4. Revert, push the fix, watch it go green and auto-deploy.
5. Refresh `http://localhost:5050/status` — the `run_id` changed, proving the new build actually redeployed.

### Step 13 — Wrap up and clean up

Talk points: CI (lint/test) vs CD (build/deploy), why an ML pipeline needs a *metrics* gate and not just a *code* gate, and how rollback works here (redeploy a prior image tag).

```bash
docker rm -f house-price-app
docker compose down -v
```
