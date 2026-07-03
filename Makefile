VENV := .venv
PYTHON := $(VENV)/bin/python3
PIP := $(VENV)/bin/pip
IMAGE_NAME := house-price-predictor
IMAGE_TAG ?= local
CONTAINER_NAME := house-price-app
PORT ?= 5050

.PHONY: setup lint test train validate build deploy smoke pipeline clean

setup:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt -r requirements-dev.txt

lint:
	$(PYTHON) -m flake8 .

test:
	$(PYTHON) -m pytest tests/ -v

train:
	$(PYTHON) train.py full

validate:
	$(PYTHON) scripts/validate_model.py

build:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

deploy:
	-docker stop $(CONTAINER_NAME)
	-docker rm $(CONTAINER_NAME)
	docker run -d --name $(CONTAINER_NAME) -p $(PORT):5000 $(IMAGE_NAME):$(IMAGE_TAG)

smoke:
	sleep 3
	curl --fail --retry 8 --retry-delay 2 --retry-all-errors http://localhost:$(PORT)/status

pipeline: lint test train validate build deploy smoke

clean:
	rm -f models/latest_model.pkl models/latest_model_info.json experiments/experiment_log.csv data/processed/house_prices_train.xlsx data/raw/house_prices_raw_v1.xlsx
