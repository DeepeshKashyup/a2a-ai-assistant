install:
	pip install -r requirements.txt

run:
	python -m app.main

lint:
	ruff check app tests

test:
	python -m pytest

smoke-logging:
	python -c "import logging; import structlog; from app.core.logging import setup_logging; setup_logging(); structlog.get_logger('smoke').info('logging smoke test', check='structlog'); logging.getLogger('smoke.stdlib').info('logging smoke test'); print('logging smoke passed')"