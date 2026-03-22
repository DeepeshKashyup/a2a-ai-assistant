install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

lint:
	ruff check app tests

test:
	python -m pytest

run-search-agent:
	uvicorn search_agent_app.main:app --host 0.0.0.0 --port 8081 --reload

smoke-logging:
	python -c "import logging; import structlog; from app.core.logging import setup_logging; setup_logging(); structlog.get_logger('smoke').info('logging smoke test', check='structlog'); logging.getLogger('smoke.stdlib').info('logging smoke test'); print('logging smoke passed')"

ingest:
	python scripts/ingest.py

seed:
	python scripts/seed_vectorstore.py