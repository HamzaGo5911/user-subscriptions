FROM python:3.10.12-slim-buster

WORKDIR .

RUN apt-get update \
    && apt-get install -y build-essential libcairo2-dev pkg-config libgirepository1.0-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "run.py","--host=0.0.0.0"]