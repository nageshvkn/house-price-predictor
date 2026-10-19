# House Price Predictor — MLOps Workshop

A short, hands-on workshop that takes one small ML application through a practical MLOps workflow:

**DVC data/pipeline versioning → MLflow experiment tracking → Jenkins CI/CD → Docker deployment**

The project uses deterministic synthetic house-price data so the workshop runs without downloading a dataset or needing cloud credentials. The goal is to learn the workflow, not to build a real estate pricing product.

## What students will learn

- How Git and DVC work together: Git stores code and pipeline metadata; DVC stores and versions data and model outputs.
- How to rerun only the pipeline stages affected by a change with `dvc repro`.
- How to compare parameters, metrics, and model artifacts in MLflow.
- How Jenkins runs tests, reproduces the ML pipeline, applies a model-quality gate, and builds/deploys a Docker image.
- How to inspect a running model service and understand the limits of a demo deployment.

## Workshop flow

1. Set up the project and its local DVC remote.
2. Run the DVC pipeline and inspect its stages.
3. Compare the MLflow training run.
4. Change a parameter and reproduce the pipeline.
5. Run the Jenkins pipeline.
6. Send a prediction to the Dockerized service and clean up.

This replaces the earlier manual generate/clean/train tour with one reproducible pipeline run. The steps below are also intended as the post-workshop student runbook.

## Prerequisites

Install these before the workshop:

- Git
- Python 3.11 or newer
- Docker Desktop (including Docker Compose)
- A terminal and a clone of this repository

Jenkins is run locally in Docker. No Jenkins server, cloud account, DagsHub account, or external dataset is required.

## 1. Set up the environment

From the project directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

On Windows PowerShell, activate with:

```powershell
.venv\Scripts\Activate.ps1
```

`requirements-dev.txt` includes the workshop tools and app dependencies from `requirements.txt`, plus lint and test tools.

Check the tools:

```bash
dvc --version
mlflow --version
```

## 2. Understand the project files

| File | Purpose |
|---|---|
| `dvc.yaml` | Declares the generate → clean → train pipeline and its dependencies/outputs. |
| `params.yaml` | Holds the data-generation and training parameters consumed by DVC. |
| `.dvc/config` | Configures the simple local DVC remote used in this workshop. |
| `data.py` | Generates deterministic synthetic data and cleans missing values. |
| `train.py` | Runs a pipeline stage and logs each training run to MLflow. |
| `model.py` | Feature transformation, linear regression, prediction, and evaluation. |
| `scripts/validate_model.py` | Stops the release if the configured R² quality threshold is not met. |
| `Jenkinsfile` | Runs checks, DVC reproduction, model validation, image build, deployment, and smoke test. |
| `docker-compose.yml` | Starts the MLflow tracking server and the local Jenkins instance. |
| `Dockerfile` | Packages the Flask prediction service with the trained model. |

## 3. Start MLflow and Jenkins

Start both services:

```bash
docker compose up -d --build
docker compose ps
```

Open:

- MLflow: <http://localhost:5001>
- Jenkins: <http://localhost:8090>

Get the first Jenkins administrator password:

```bash
docker compose logs jenkins
```

Find the line containing `initialAdminPassword`, then complete the Jenkins setup wizard and install the suggested plugins.

For local training, MLflow is available at `http://127.0.0.1:5001`. Jenkins uses the Compose network address `http://mlflow:5001`.

## 4. Configure the local DVC remote

DVC stores large pipeline outputs outside Git. For this laptop workshop, the repository is preconfigured to use a local directory in the project folder, excluded from Git:

```text
house-price-predictor-dvc-storage/
```

Create it and upload the current DVC-tracked outputs if any exist:

```bash
mkdir -p house-price-predictor-dvc-storage
dvc remote list
dvc push
```

This local remote is a teaching convenience, not shared team storage. For a team workshop, replace it with a shared DVC remote (for example, DagsHub or cloud object storage) and configure credentials securely; never commit tokens or passwords.

## 5. Run the reproducible ML pipeline

Point this terminal at the MLflow server and run the pipeline:

```bash
export MLFLOW_TRACKING_URI=http://127.0.0.1:5001
dvc repro
```

On Windows PowerShell, set the environment variable with:

```powershell
$env:MLFLOW_TRACKING_URI = "http://127.0.0.1:5001"
dvc repro
```

DVC executes three stages:

1. **generate** — creates synthetic raw data with a fixed seed.
2. **prepare** — fills missing values and saves the processed dataset.
3. **train** — fits a linear regression model, calculates RMSE/MAE/R², saves the model, and logs parameters, metrics, and the model artifact to MLflow.

Useful commands:

```bash
dvc dag       # display the stage dependency graph
dvc status    # see whether inputs or outputs have changed
dvc metrics show
dvc push      # upload data/model outputs to the configured remote
```

Open <http://localhost:5001> and select the `house-price-predictor` experiment. Compare the run parameters and metrics. The `models/latest_model.pkl` file is used by the web app; MLflow keeps the per-run model artifact and history.

## 6. Change a parameter and reproduce

Edit `params.yaml`, for example change `data.rows` from `150` to `200`, then run:

```bash
dvc repro
```

DVC detects which stages depend on the changed parameter and reruns only those stages. Inspect the new run in MLflow and compare its metrics with the previous run. Restore the original value afterward if you want the default workshop state.

Try changing `train.test_size` as a second exercise. Discuss why changing the data split can change evaluation metrics, and why experiments should record their parameters.

## 7. Run checks and build the service

Run the same checks Jenkins will use:

```bash
make lint
make test
make reproduce
make validate
make build
```

To run the container locally after a successful build:

```bash
make deploy
make smoke
```

Each Jenkins build tags its image with the build number. If you need to restore a previously built image, stop the current container and run the earlier tag:

```bash
make rollback IMAGE_TAG=<previous-build-number>
make smoke
```

The model quality gate reads `models/latest_model_info.json`. To demonstrate a failing release, temporarily raise `MIN_R2` in `scripts/validate_model.py` above the model's measured R², then run:

```bash
make validate
```

The gate should fail. Restore the threshold before continuing.

## 8. Create a Jenkins pipeline

In Jenkins:

1. Select **New Item**, name it `house-price-predictor`, choose **Pipeline**, and select **OK**.
2. Under **Pipeline**, choose **Pipeline script from SCM**.
3. Select **Git**, enter the Git repository URL, set the branch (for example `*/main`), and set **Script Path** to `Jenkinsfile`.
4. Save, then select **Build Now**.

The Jenkinsfile runs lint, unit tests, DVC reproduction, model validation, Docker build, deployment, and a smoke test in that order. The quality gate runs before image build and deployment, so a model below the threshold cannot be released.
Deployment replaces the local container, so a failure during the deploy/smoke stages may require the manual rollback command above.

For a push-triggered demo, configure a webhook in your Git host. Polling SCM is an alternative for a local workshop, but avoid a one-minute poll interval on a shared Jenkins server.

The provided Jenkins container mounts Docker Desktop's Docker socket so the pipeline can build and run containers. This is intended only for a trusted local workshop; access to the Docker socket is effectively privileged access to the host.

## 9. Try the deployed predictor

After the pipeline succeeds, open <http://localhost:5050/> and submit property details. You can also check:

```bash
curl http://localhost:5050/status
```

The status response includes the MLflow run ID and the model evaluation metrics. The prediction endpoint accepts form-encoded values:

```bash
curl -X POST http://localhost:5050/predict \
  -d "area=1800&bedrooms=3&bathrooms=2&location=Urban"
```

## 10. Push DVC outputs and clean up

Store the resulting data and model outputs in the configured DVC remote:

```bash
dvc push
```

Stop the local services when finished:

```bash
docker compose down
```

To also delete Jenkins and MLflow history stored in Compose volumes, use:

```bash
docker compose down -v
```

This permanently removes those local service volumes. Do not use `-v` if you want to keep the MLflow run history or Jenkins configuration.

## Troubleshooting

### Port 5000 or 5050 is already in use

Stop the other app using that port, or change the host port in the `deploy` and `smoke` targets in the `Makefile`.

### MLflow is not reachable

Check that the service is running:

```bash
docker compose ps
docker compose logs mlflow
```

For local training, confirm `MLFLOW_TRACKING_URI` is set to `http://127.0.0.1:5001`. Jenkins must use `http://mlflow:5001` from inside the Compose network.

### DVC says outputs are missing

Run the pipeline first with `dvc repro`. If the outputs should already exist in the remote, run `dvc pull`.

### Jenkins cannot build or run Docker images

Confirm Docker Desktop is running and the Docker socket mount is enabled. The Jenkins container in this workshop is intentionally configured for a local Docker Desktop environment.

## Scope and production notes

This is a teaching project with synthetic data and a simple linear regression model. Its R² gate is an example of a release check, not evidence that the model is suitable for real pricing decisions. A production system would need representative data, stronger validation, model/data monitoring, secure CI credentials, controlled model promotion, and production-grade serving and deployment.
