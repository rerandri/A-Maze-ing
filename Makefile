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
	mypy . --warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

build:
	$(PYTHON) -m build

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || True
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || True
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || True
	find . -type d -name "$(BUILD_DIR)" -exec rm -rf {} + 2>/dev/null || True
	find . -type d -name "*.pyc" -exec rm -rf {} + 2>/dev/null || True
	@echo "Cleaned"


.PHONY: all install run lint lint-strict build clean debug
