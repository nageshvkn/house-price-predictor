FROM python:3.13-slim

WORKDIR /app

COPY requirements-app.txt .
RUN pip install --no-cache-dir -r requirements-app.txt

COPY app.py config.py model.py ./
COPY templates/ templates/
COPY models/ models/

EXPOSE 5000
ENV PORT=5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
