.PHONY: help install test lint typecheck run run-otel compose-build compose-up compose-down compose-logs compose-ps pre-commit

COMPOSE ?= docker-compose
APP_API_TOKEN ?= local-api-token
APP_SIGNING_KEY ?= local-signing-key
APP_OTEL_LOGS_ENDPOINT ?= http://localhost:4318/v1/logs
APP_OTEL_METRICS_ENDPOINT ?= http://localhost:4318/v1/metrics
APP_OTEL_TRACES_ENDPOINT ?= http://localhost:4318/v1/traces
OTEL_METRIC_EXPORT_INTERVAL ?= 1000

help:
	@printf "%s\n" \
		"Available commands:" \
		"  make install       - Install dependencies with uv" \
		"  make test          - Run pytest" \
		"  make run           - Run the app locally" \
		"  make run-otel      - Run the app with a local OTel collector" \
		"  make lint          - Run ruff" \
		"  make typecheck     - Run mypy" \
		"  make compose-build - Build the local compose images" \
		"  make compose-up    - Start the local app and collector stack" \
		"  make compose-down  - Stop the local compose stack" \
		"  make compose-logs  - Tail compose service logs" \
		"  make compose-ps    - Show compose service status" \
		"  make pre-commit    - Run lint, typecheck, and test"

install:
	uv sync

test:
	uv run pytest -v

lint:
	uv run ruff check .

typecheck:
	uv run mypy .

run:
	APP_API_TOKEN="123" APP_SIGNING_KEY="123" uv run main.py

run-otel:
	APP_API_TOKEN="123" APP_SIGNING_KEY="123" APP_LOGGING_LEVEL=WARNING APP_OTEL_LOGS_ENDPOINT="$(APP_OTEL_LOGS_ENDPOINT)" APP_OTEL_METRICS_ENDPOINT="$(APP_OTEL_METRICS_ENDPOINT)" APP_OTEL_TRACES_ENDPOINT="$(APP_OTEL_TRACES_ENDPOINT)" OTEL_METRIC_EXPORT_INTERVAL="$(OTEL_METRIC_EXPORT_INTERVAL)" uv run main.py

compose-build:
	$(COMPOSE) build

compose-up:
	$(COMPOSE) up --build -d

compose-down:
	$(COMPOSE) down --remove-orphans

compose-logs:
	$(COMPOSE) logs -f app otel-collector

compose-ps:
	$(COMPOSE) ps

pre-commit: lint typecheck test
