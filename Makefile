# Variables
PYTHON = python3
PIP = pip3
REQUIREMENTS_FILE = requirements.txt

# Targets
.PHONY: install run clean test

install:
	$(PIP) install -r $(REQUIREMENTS_FILE)

run:
	uvicorn product_navigator.api.main:app --reload

clean:
	find . -type d -name __pycache__ -exec rm -rf {} \;
	rm -rf .mypy_cache
	rm -rf .pytest_cache

test:
	coverage run -m pytest
