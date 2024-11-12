SHELL := /bin/bash

.PHONY: setup test run docker-build docker-run clean

setup:
		python3 -m venv ragnarock && \
		. ./ragnarock/bin/activate && \
		pip install -r requirements.txt

test:
		pytest tests/ -v

run:
		uvicorn src.api.main:app --reload --port 8000

docker-build:
		docker build -t infra-rag .

docker-run:
		docker run -p 8000:8000 --env-file .env infra-rag

clean:
		rm -rf ragnarock/
		find . -type d -name "__pycache__" -exec rm -rf {} +
		find . -type f -name "*.pyc" -delete
		find . -type d -name ".pytest_cache" -exec rm -rf {} +