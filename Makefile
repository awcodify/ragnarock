.PHONY: setup test run docker-build docker-run

setup:
		python3 -m venv ragnarock
		. ragnarock/bin/activate && pip install -r requirements.txt
		. ragnarock/bin/activate && pip install -e .

test:
		pytest tests/ -v

run:
		uvicorn src.api.main:app --reload --port 8000

docker-build:
		docker build -t infra-rag .

docker-run:
		docker run -p 8000:8000 --env-file .env infra-rag