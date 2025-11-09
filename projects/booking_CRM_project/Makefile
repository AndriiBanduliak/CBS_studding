PY = python
PIP = pip

# Backend
.PHONY: venv install migrate run createsuperuser shell

venv:
	$(PY) -m venv .venv

install:
	. ./.venv/Scripts/activate && $(PIP) install -r requirements.txt
	. ./.venv/Scripts/activate && $(PIP) install -r requirements-dev.txt

migrate:
	. ./.venv/Scripts/activate && $(PY) manage.py migrate

run:
	. ./.venv/Scripts/activate && $(PY) manage.py runserver 0.0.0.0:8000

createsuperuser:
	. ./.venv/Scripts/activate && $(PY) manage.py createsuperuser

shell:
	. ./.venv/Scripts/activate && $(PY) manage.py shell

# Frontend
.PHONY: fe-install fe-dev fe-build fe-types

fe-install:
	cd frontend && npm install

fe-dev:
	cd frontend && npm run dev -- --host

fe-build:
	cd frontend && npm run build

fe-types:
	cd frontend && npm run types

# QA
.PHONY: test lint precommit-install

test:
	. ./.venv/Scripts/activate && pytest -q

lint:
	. ./.venv/Scripts/activate && ruff . && isort --check . && black --check .

precommit-install:
	. ./.venv/Scripts/activate && pre-commit install


