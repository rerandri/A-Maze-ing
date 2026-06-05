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
MLX_SRC ?= mlx_CLXV-2.2
MLX_TGZ ?= $(MLX_SRC).tgz

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

# -----------------------------------------------------------------------
# MiniLibX (42 graphical library) — compilation & installation
# -----------------------------------------------------------------------
# Décompresse, compile la bibliothèque C et installe le wrapper Python
# dans le site-packages de l'interpréteur courant.
#
# Prérequis :  libX11-dev libXext-dev libXrandr-dev (Debian/Ubuntu)
#              xdotool
#
# Usage :  make mlx-install
#          make mlx-install MLX_TGZ=~/Downloads/mlx_CLXV-2.2.tgz
# -----------------------------------------------------------------------

mlx-install: $(MLX_TGZ)
	@echo "=== Compilation de MiniLibX ==="
	rm -rf /tmp/$(MLX_SRC)
	tar xzf "$(MLX_TGZ)" -C /tmp
	$(MAKE) -C /tmp/$(MLX_SRC)
	@echo "=== Installation du wrapper Python ==="
	PY_VER=$$($(PYTHON) -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"); \
	PKG_DIR=$$HOME/.local/lib/python$$PY_VER/site-packages/mlx; \
	mkdir -p $$PKG_DIR; \
	cp /tmp/$(MLX_SRC)/libmlx.so $$PKG_DIR/; \
	cp display/mlx.py $$PKG_DIR/; \
	echo "Copied libmlx.so -> $$PKG_DIR/"
	rm -rf /tmp/$(MLX_SRC)
	@echo "✅ MiniLibX installé. Lancez: make run"

$(MLX_TGZ):
	@echo "Erreur: fichier $(MLX_TGZ) introuvable."
	@echo "Téléchargez mlx_CLXV depuis l'intra 42 et placez-le à la racine."
	@echo "Ou specifiez le chemin: make mlx-install MLX_TGZ=/chemin/vers/mlx_CLXV-2.2.tgz"
	exit 1

.PHONY: all install run lint lint-strict test build clean mlx-install debug
