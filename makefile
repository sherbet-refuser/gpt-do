PYTHON := python3.12

LINT_TARGETS := gpt_do

.PHONY: do
do:
	.venv/bin/python3 -m gpt_do

.PHONY: env
env:
	${PYTHON} -m venv .venv
	.venv/bin/python3 -m pip install -U pip -q
	.venv/bin/python3 -m pip install -r requirements.txt -U -q

.PHONY: flake8
flake8:
	.venv/bin/flake8 ${LINT_TARGETS}

.PHONY: pylint
pylint:
	.venv/bin/pylint ${LINT_TARGETS}

.PHONY: mypy
mypy:
	.venv/bin/mypy ${LINT_TARGETS}

.PHONY: isort
isort:
	.venv/bin/isort ${LINT_TARGETS}

.PHONY: isort-check
isort-check:
	.venv/bin/isort --check ${LINT_TARGETS}

.PHONY: black
black:
	.venv/bin/black ${LINT_TARGETS}

.PHONY: black-check
black-check:
	.venv/bin/black --check ${LINT_TARGETS}

.PHONY: format
format: isort black

.PHONY: lint
lint: flake8 pylint mypy isort-check black-check
