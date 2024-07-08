FROM python:3.10.6

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .
COPY logger.py .
COPY db.py .
COPY routes.py .
COPY query.py .
