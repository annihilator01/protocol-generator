WEB_CONTAINER_NAME := $(shell docker ps --format "{{.Names}}" | grep crawler_web_server)

.PHONY: init
init:
	cp .env.example .env
	@echo ".env file created, change values if it is necessary"

.PHONY: venv
venv:
	python3 -m venv ./venv
	. ./venv/bin/activate
	pip install -r requirements.txt

.PHONY: postgres
postgres:
	docker compose up --build --remove-orphans postgres

.PHONY: help
help:
	@echo "make init:     initializing environment variables      "
	@echo "make venv:     create python venv with all dependencies"
	@echo "make postgres: run postgres in docker container        "
	@echo "make help:     show this help                          "