#make install      # installe flake8, mypy, build, pytest
#make run          # python3 a_maze_ing.py config.txt
#make debug        # pdb
#make lint         # flake8 + mypy standard
#make lint-strict  # flake8 + mypy --strict
#make test         # pytest
#make build        # génère le .whl
#make mlx-install  # compile et installe MiniLibX
#make clean        # nettoie __pycache__, dist, etc.

PYTHON = python3
PIP = pip3
MAIN = a_maze_ing.py
CONFIG = config.txt
BUILD_DIR = dist


all: install

install:
	$(PIP) install --break-system-packages flake8 mypy build pytest

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

test:
	$(PYTHON) -m pytest -v

build:
	$(PYTHON) -m build
	@echo "Package built in $(BUILD_DIR)/"

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || True
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || True
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || True
	find . -type d -name "$(BUILD_DIR)" -exec rm -rf {} + 2>/dev/null || True
	find . -type d -name "*.pyc" -exec rm -rf {} + 2>/dev/null || True
	@echo "Cleaned"


.PHONY: all install run lint lint-strict test build clean debug
