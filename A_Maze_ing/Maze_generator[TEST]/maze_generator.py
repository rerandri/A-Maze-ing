# donne necessaires pour une labyrinthe:
# - taille du labyrinthe : size [Width: int, Height: int]
# - position de départ : entry [x: int, y: int]
# - position de sortie : exit [x: int, y: int]
# - seed pour la génération aléatoire : seed [int | none] optionel
# - sortie du labyrinthe du format : output_file [maze.txt]

import random

class MazeGenerator:
    # Initialisation de la classe MazeGenerator
    NORTH: int = 1  # 0001
    EAST: int = 2   # 0010
    SOUTH: int = 4  # 0100
    WEST: int = 8   # 1000

    # Initial de 42
    PATTERN_42: list[str] = [
        "F000FFF",
        "F00000F",
        "FFF0FFF",
        "00F0F00",
        "00F0FFF",
    ]

    # Dictionnaire pour les directions opposées
    OPPOSITE: dict[int, int] = {
        NORTH: SOUTH,
        SOUTH: NORTH,
        EAST: WEST,
        WEST: EAST
    }

    # Delta pour les mouvements dans les directions
    DELTA: dict[int, tuple[int, int]] = {
        NORTH: (0, -1),
        EAST: (1, 0),
        SOUTH: (0, 1),
        WEST: (-1, 0)
    }

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit: tuple[int, int],
        seed: int | None = None
    ) -> None:

        self.width: int = width
        self.height: int = height
        self.entry: tuple[int, int] = entry
        self.exit: tuple[int, int] = exit
        self.seed: int | None = random.randint(0, 2**32) if seed is None else seed
        self._blocked: set[tuple[int, int]] = set()
        self._solution: list[str] = []
        self._generated: bool = False

    def _init_grid(self) -> None:
        # addition des binaires pour les murs [1,1,1,1] = 15 en hex : 0xF
        closed: int = self.NORTH | self.EAST | self.SOUTH | self.WEST
        for cell in range(self.height):
            self.grid.append([closed] * self.width)

    def _remove_wall(
        self,
        x1: int, y1: int, wto_remove: int, # mur à enlever
        x2: int, y2: int, wto_add: int,    # mur à ajouter
    ):
        self.grid[y1][x1] &= ~wto_remove
        self.grid[y2][x2] &= ~wto_add

    def _in_bounds(self, x: int, y: int) -> bool:
        # vérifie si les coordonnées sont dans les limites du labyrinthe
        return 0 <= x < self.width and 0 <= y < self.height

    def _require_generated(self) -> None:
        # signale une erreur si le labyrinthe n'a pas encore été généré
        if not self._generated:
            raise Exception("Maze not generated yet. Call generate() first.")

    def get_cell(self, x: int, y: int) -> int:
        self._require_generated()
        if not self._in_bounds(x, y):
            raise IndexError("Cell coordinates out of bounds.")
        return self.grid[y][x] # ex: grid[12][34] pour accéder à la cellule à (34, 12)

    def has_wall(self, x: int, y: int, direction: int) -> bool:
        self._require_generated()
        if not self._in_bounds(x, y):
            raise IndexError("Cell coordinates out of bounds.")
        cellule: int = self.grid[y][x]
        # ex: grid[y][x] = 15 (0xF) pour une cellule fermée
    # vérifie si le mur dans la direction spécifiée est présent (1) ou absent (0)
        return (cellule & direction) != 0

    def _has_wall(self, x: int, y: int, direction: int) -> bool:
        # Considérer les murs hors limites comme présents
        if not self._in_bounds(x, y):
            return True
        # vérifie si le mur dans la direction spécifiée est présent (1) ou absent (0)
        cellule: int = self.grid[y][x]
        return (cellule & direction) != 0

    def _generated_dfs(self) -> None:
        stack: list[tuple[int, int]] = [self.entry]
        visited: set[tuple[int, int]] = {self.entry}

        while stack:
            # Récupère la position actuelle du sommet de la pile
            current_x, current_y = stack[-1]
            neighbors = []
        # boucle pour trouver les voisins non visités de la cellule actuelle
            # Pour chaque direction, calcule les coordonnées du voisin
            # et vérifie s'il n'a pas été visité et s'il est dans les limites du labyrinthe
            for direction, (dir_x, dir_y) in self.DELTA.items():
                # deplacement dans la direction actuelle
                next_x = current_x + dir_x
                next_y = current_y + dir_y
                if (
                    self._in_bounds(next_x, next_y)           # vérifier les limites du labyrinthe
                    and (next_x, next_y) not in visited       # éviter les cellules déjà visitées
                    and (next_x, next_y) not in self._blocked # éviter les cellules bloquées (ex: celles utilisées pour le pattern 42
                ):
                    neighbors.append((direction, next_x, next_y))
        # Verifie s'il y a des voisins disponibles pour continuer la génération
            if neighbors:
                next_x, next_y, direction = random.choice(neighbors)
                # Choisir un voisin aléatoire parmi les disponibles
                self._remove_wall(
                    current_x,       # coordonnées de la cellule actuelle
                    current_y,       # coordonnées de la cellule actuelle
                    direction,       # mur à enlever de la cellule actuelle
                    self.OPPOSITE[direction] # mur à enlever de la cellule voisine (opposé à la direction actuelle)
                )
                visited.add((next_x, next_y)) # marquer le voisin comme visité
                stack.append((next_x, next_y)) # ajouter le voisin à la pile pour continuer
            else:
                stack.pop() # revenir en arrière si aucun voisin n'est disponible
        # En resumer:
        # 1. Commence à la position d'entrée et marque-la comme visitée.
        # 2. Tant que la pile n'est pas vide, regarde le sommet de la pile pour trouver les voisins non visités.
        # 3. Si des voisins sont disponibles, en choisit un au hasard, enlève les murs entre la cellule actuelle et le voisin, marque le voisin comme visité, et ajoute le voisin à la pile.
        # 4. Si aucun voisin n'est disponible, retire la cellule actuelle de la pile pour revenir en arrière.
