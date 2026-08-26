FROM python:3.11-slim

WORKDIR /app

COPY src/requirements.txt /app/src/requirements.txt

RUN pip install --no-cache-dir -r /app/src/requirements.txt

RUN playwright install --with-deps chromium

COPY src /app/src

RUN mkdir -p /app/Data /app/logs

CMD ["python", "src/pipeline.py"]