FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py config.py model.py ./
COPY templates/ templates/
COPY models/ models/

EXPOSE 5000
ENV PORT=5000

CMD ["python3", "app.py"]
