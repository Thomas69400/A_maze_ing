PYTHON := python3
PIP := $(PYTHON) -m pip
MAIN_SCRIPT := main.py
PROJECT_NAME := mazegen
VENV := .venv

help:
	@echo "Available commands:"
	@echo "  make setup        - Create virtual environment and install build tools"
	@echo "  make install      - Install project dependencies"
	@echo "  make run          - Execute the main script"
	@echo "  make debug        - Run the main script in debug mode (pdb)"
	@echo "  make clean        - Remove temporary files and caches"
	@echo "  make lint         - Run flake8 and mypy with standard checks"
	@echo "  make lint-strict  - Run flake8 and mypy with strict mode"
	@echo "  make build        - Build the Python package"
	@echo "  make help         - Show this help message"

install:
	$(PIP) install --upgrade pip setuptools wheel || true
	# Try installing requirements from dependencies/, but don't abort on failure
	$(PIP) install -r dependencies/requirements.txt || echo "Warning: some packages from dependencies/requirements.txt failed to install"
	# Install any local wheels present (no-op if none)
	$(PIP) install dependencies/*.whl || echo "No local .whl files found in dependencies/"

run:
	$(PYTHON) $(MAIN_SCRIPT)

debug:
	$(PYTHON) -m pdb $(MAIN_SCRIPT)

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name *.egg-info -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	rm -rf build/ dist/ 2>/dev/null || true

lint:
	flake8 . --exclude=.git,.venv,venv,env,test_vm,build,dist,.mypy_cache,.pytest_cache,__pycache__,dependencies,src,*.egg-info
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports \
		--disallow-untyped-defs --check-untyped-defs --exclude='(build|dist|venv|env|test_vm|dependencies|src)'

lint-strict:
	flake8 . --exclude=.git,.venv,venv,env,test_vm,build,dist,.mypy_cache,.pytest_cache,__pycache__,dependencies,src,*.egg-info
	mypy . --strict --exclude='(build|dist|venv|env|test_vm|dependencies|src)'

build: clean
	# Ensure pip (bootstrap if necessary) and install build tools, tolerant to missing pip
	$(PYTHON) -m pip install --upgrade build setuptools wheel 2>/dev/null || { \
		echo "pip not available for $(PYTHON), attempting to bootstrap..."; \
		$(PYTHON) -m ensurepip --upgrade >/dev/null 2>&1 || curl -sS https://bootstrap.pypa.io/get-pip.py | $(PYTHON); \
		$(PYTHON) -m pip install --upgrade build setuptools wheel; \
	}
	$(PYTHON) -m build

setup:
	@rm -rf $(VENV) 2>/dev/null || true
	# Create venv with pip available; if pip still missing, bootstrap it
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/python -m pip --version >/dev/null 2>&1 || curl -sS https://bootstrap.pypa.io/get-pip.py | $(VENV)/bin/python
	$(VENV)/bin/pip install --upgrade pip setuptools wheel build
	@echo ""
	@echo "Virtual environment created in $(VENV)/"
	@echo "To activate it, run:"
	@echo "  source $(VENV)/bin/activate"

.DEFAULT_GOAL := help

.PHONY: install run debug clean lint lint-strict build help setup