FROM python:3.13-slim

RUN pip install --no-cache-dir "mlflow==3.17.1"

WORKDIR /mlflow
EXPOSE 5001

CMD ["mlflow", "server", "--host", "0.0.0.0", "--port", "5001", \
     "--backend-store-uri", "sqlite:////mlflow/mlflow.db", \
     "--artifacts-destination", "/mlflow/artifacts", \
     "--allowed-hosts", "localhost:5001,127.0.0.1:5001,mlflow:5001,mlops-mlflow:5001,host.docker.internal:5001"]
