VENV := .venv
PYTHON := $(VENV)/bin/python3
PIP := $(VENV)/bin/pip
IMAGE_NAME := house-price-predictor
IMAGE_TAG ?= local
CONTAINER_NAME := house-price-app
PORT ?= 5050

.PHONY: setup lint test reproduce train validate build deploy smoke pipeline clean rollback

setup:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-dev.txt

lint:
	$(PYTHON) -m flake8 .

test:
	$(PYTHON) -m pytest tests/ -v

reproduce:
	PATH="$(CURDIR)/$(VENV)/bin:$$PATH" $(PYTHON) -m dvc repro

train: reproduce

validate:
	$(PYTHON) scripts/validate_model.py

build:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

deploy:
	-docker rm -f $(CONTAINER_NAME)
	docker run -d --name $(CONTAINER_NAME) -p $(PORT):5000 $(IMAGE_NAME):$(IMAGE_TAG)

smoke:
	sleep 3
	curl --fail --retry 8 --retry-delay 2 --retry-all-errors http://$(APP_HOST):$(PORT)/status

APP_HOST ?= localhost

pipeline: lint test reproduce validate build deploy smoke

rollback:
	@test "$(IMAGE_TAG)" != "local" || (echo "Set IMAGE_TAG to a previous image tag"; exit 1)
	-docker rm -f $(CONTAINER_NAME)
	docker run -d --name $(CONTAINER_NAME) -p $(PORT):5000 $(IMAGE_NAME):$(IMAGE_TAG)

clean:
	-docker rm -f $(CONTAINER_NAME)
