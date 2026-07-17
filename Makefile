PYTHON = python3
PIP = pip3
MAIN = a_maze_ing.py
CONFIG = config.txt

all: install

install:
	$(PIP) install --break-system-packages flake8 mypy build

run:
	$(PYTHON) $(MAIN) $(CONFIG)

lint:
	flake8 .
	mypy . --strict

build:
	$(PYTHON) -m build

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.pyc" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleaned"

.PHONY: all install run lint build debug clean
