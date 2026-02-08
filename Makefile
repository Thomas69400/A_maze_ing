PYTHON := python3
PIP := pip
MAIN_SCRIPT := main.py
PROJECT_NAME := mazegen

help:
	@echo "Available commands:"
	@echo "  make install      - Install project dependencies"
	@echo "  make run          - Execute the main script"
	@echo "  make debug        - Run the main script in debug mode (pdb)"
	@echo "  make clean        - Remove temporary files and caches"
	@echo "  make lint         - Run flake8 and mypy with standard checks"
	@echo "  make lint-strict  - Run flake8 and mypy with strict mode"
	@echo "  make build        - Build the Python package"
	@echo "  make help         - Show this help message"

install:
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -r dependencies/requirements.txt

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
	$(PYTHON) -m pip install --upgrade build setuptools wheel
	$(PYTHON) -m build

.DEFAULT_GOAL := help

.PHONY: install run debug clean lint lint-strict build help