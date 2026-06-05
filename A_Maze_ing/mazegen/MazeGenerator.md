# Explication détaillée du MazeGenerator

## Aperçu général

`MazeGenerator` est le cœur de la génération de labyrinthe. Il implémente :
- Un système de **murs par bits** (bitmask) pour chaque cellule
- La génération par **parcours en profondeur (DFS)** récursif (backtracking)
- Le calcul du plus court chemin par **parcours en largeur (BFS)**
- Un motif **"42"** intégré dans le labyrinthe
- La gestion des **cellules bloquées**

---

## Représentation des murs — Système de bitmask

```python
NORTH: int = 1   # 0001
EAST:  int = 2   # 0010
SOUTH: int = 4   # 0100
WEST:  int = 8   # 1000
```

Chaque cellule du labyrinthe stocke un entier dont les bits indiquent quels murs sont présents.

**Exemple :** Une cellule avec tous les murs fermés :
```python
fermé = NORTH | SOUTH | EAST | WEST  # 1 | 4 | 2 | 8 = 15 (0b1111)
```

Une cellule avec seulement le mur Nord et le mur Est :
```python
nord_est = NORTH | EAST  # 1 | 2 = 3 (0b0011)
```

**Pourquoi des bits ?** Permet de manipuler les murs très efficacement avec des opérateurs bit à bit :
- `cell & NORTH` → teste si le mur Nord est présent
- `cell &= ~NORTH` → supprime le mur Nord

---

## `_init_grid` — Initialisation de la grille

```python
def _init_grid(self) -> None:
    closed = self.NORTH | self.SOUTH | self.EAST | self.WEST  # 15
    self.grid = [[closed for _ in range(self.width)]
                 for _ in range(self.height)]
```

**Rôle :** Crée une grille où chaque cellule a **tous ses murs fermés** (valeur 15). C'est l'état de départ avant le creusement des passages.

**Exemple** pour un labyrinthe 3×3 :
```python
grid = [
    [15, 15, 15],   # ligne 0 : toutes les fermées
    [15, 15, 15],   # ligne 1 : toutes les fermées
    [15, 15, 15],   # ligne 2 : toutes les fermées
]
```

---

## `_remove_wall` — Suppression d'un mur

```python
def _remove_wall(self, x1, y1, wto_open1, x2, y2, wto_open2):
    self.grid[y1][x1] &= ~wto_open1
    self.grid[y2][x2] &= ~wto_open2
```

**Rôle :** Supprime les murs entre deux cellules adjacentes (opération inverse : enlève le bit).

**Exemple :** Supprimer le mur Est de la cellule (0,0) et le mur Ouest de la cellule (1,0) :
```python
# Avant : grid[0][0] = 15 (binaire 1111)
#         grid[0][1] = 15 (binaire 1111)
_remove_wall(0, 0, EAST, 1, 0, WEST)
# grid[0][0] = 15 & ~2 = 13 (binaire 1101) — plus de mur Est
# grid[0][1] = 15 & ~8 = 7  (binaire 0111) — plus de mur Ouest
```

---

## Génération du labyrinthe — `generate`

```python
def generate(self) -> None:
    self._init_grid()
    random.seed(self.seed)
    self._carve_pattern42()    # Étape 1 : motif 42
    self._generate_dfs()        # Étape 2 : creuser passages
    self._solve_bfs()           # Étape 3 : trouver solution
    self._generated = True
```

**Ordonnancement :**
1. Initialiser la grille (tous murs fermés)
2. Fixer la graine aléatoire (reproductibilité)
3. Marquer les cellules bloquées du motif "42"
4. Creuser les passages avec DFS (en évitant les bloquées)
5. Calculer le chemin solution avec BFS
6. Marquer comme généré

---

## Motif "42" — `_carve_pattern42`

```python
PATTERN_42: list[str] = [
    "F000FFF",
    "F00000F",
    "FFF0FFF",
    "00F0F00",
    "00F0FFF",
]
```

**Rôle :** Dessine le motif "42" au centre du labyrinthe en marquant certaines cellules comme bloquées.

**Logique :**
1. La grille de motif fait 7 colonnes × 5 lignes
2. Chaque `"F"` dans le motif → cellule bloquée (le chemin ne peut pas passer)
3. Chaque `"0"` → cellule libre
4. Le motif est centré : `start_x = (width - 7) // 2`, `start_y = (height - 5) // 2`

**Exemple visuel** du motif (F = bloqué, . = libre) :
```
F F F . . F F F    →  ligne 0 : "F000FFF"
F . . . . . F      →  ligne 1 : "F00000F"
F F F . F F F      →  ligne 2 : "FFF0FFF"
. . F . F . .      →  ligne 3 : "00F0F00"
. . F . F F F      →  ligne 4 : "00F0FFF"
```

Ce motif forme les chiffres **4** et **2** quand on regarde les cellules bloquées.

---

## Creusement des passages — `_generate_dfs` (recursive backtracker)

```python
def _generate_dfs(self) -> None:
    stack: list[tuple[int, int]] = [self.entry]
    visited: set[tuple[int, int]] = {self.entry}

    while stack:
        current_x, current_y = stack[-1]
        neighbors = []
        for direction, (dx, dy) in self.DELTA.items():
            nx, ny = current_x + dx, current_y + dy
            if (self._in_bounds(nx, ny)
                and (nx, ny) not in visited
                and (nx, ny) not in self._blocked):
                neighbors.append((nx, ny, direction))

        if neighbors:
            next_x, next_y, direction = random.choice(neighbors)
            self._remove_wall(current_x, current_y, direction,
                            next_x, next_y, self.OPPOSITE[direction])
            visited.add((next_x, next_y))
            stack.append((next_x, next_y))
        else:
            stack.pop()
```

**Algorithme :** **Recursive backtracker** (parcours en profondeur avec backtracking)

**Logique :**
1. On part de l'entrée, ajoutée à la pile et marquée visitée
2. Tant que la pile n'est pas vide :
   - On regarde la cellule en haut de la pile
   - On liste les voisins non visités et non bloqués
   - **S'il y en a** : on en choisit un au hasard, on supprime le mur entre la cellule courante et ce voisin, on marque le voisin visité, on l'empile
   - **Sinon** : on dépile (backtrack)
3. Quand la pile est vide, toutes les cellules accessibles sont visitées

**Propriétés :**
- Garantit un labyrinthe **parfait** : chaque cellule est accessible depuis n'importe quelle autre
- Pas de boucles (graphe connexe sans cycle)
- Le chemin est unique entre deux points donnés

**Exemple** pour un labyrinthe 3×3 (entrée en (0,0)) :
```
État initial :
┌───┬───┬───┐
│   │   │   │
├───┼───┼───┤
│   │   │   │
├───┼───┼───┤
│   │   │   │
└───┴───┴───┘

Après DFS (exemple) :
┌───┬───┬───┐
│   │   │   │
├───┼───┼───┤
│       │   │
├───┼───┼───┤
│       │   │
└───┴───┴───┘
```

---

## Résolution du chemin — `_solve_bfs`

```python
def _solve_bfs(self) -> None:
    queue: deque[tuple[int, int]] = deque([self.entry])
    parent: dict = {self.entry: ((-1, -1), 0)}

    while queue:
        x, y = queue.popleft()
        if (x, y) == self.exit:
            # reconstruction du chemin
            path = []
            curr = self.exit
            while curr != self.entry:
                prev, direction = parent[curr]
                direction_names = {NORTH: "N", SOUTH: "S", EAST: "E", WEST: "W"}
                path.append(direction_names[direction])
                curr = prev
            path.reverse()
            self._solution = path
            return

        for direction, (dx, dy) in self.DELTA.items():
            nx, ny = x + dx, y + dy
            if (self._in_bounds(nx, ny)
                and not self._has_wall_internal(x, y, direction)
                and (nx, ny) not in parent):
                parent[(nx, ny)] = ((x, y), direction)
                queue.append((nx, ny))
```

**Algorithme :** **BFS** (Breadth-First Search) — parcours en largeur

**Logique :**
1. Initialise une file avec l'entrée
2. Pour chaque cellule visitée, on explore les voisins accessibles (sans mur entre eux) dans les 4 directions
3. On stocke le parent de chaque cellule et la direction empruntée
4. Dès qu'on atteint la sortie, on reconstruit le chemin en remontant les parents
5. Le résultat est une liste de chaînes : `["E", "E", "S", "S", ...]`

**Pourquoi BFS plutôt que DFS ?** BFS garantit le **plus court chemin** en nombre de pas (contrairement à DFS qui donnerait un chemin quelconque).

**Exemple :** Pour un labyrinthe simple 2×2 :
```
Entrée (0,0) → sortie (1,1)
Chemin BFS possible : ["E", "S"] ou ["S", "E"] (selon la configuration des murs)
```

---

## `has_wall` — Test de mur

```python
def has_wall(self, x: int, y: int, direction: int) -> bool:
    cell = self.get_cell(x, y)
    return (cell & direction) != 0
```

**Rôle :** Vérifie si un mur existe dans une direction donnée pour une cellule.

**Exemple :** `maze.has_wall(3, 5, MazeGenerator.NORTH)` :
- Récupère `grid[5][3]` (valeur entière, ex: 7)
- Teste le bit NORTH (1) : `7 & 1 = 1` → True, le mur Nord existe

---

## `get_solution` — Chemin solution

```python
def get_solution(self) -> list[str]:
    self._require_generated()
    return list(self._solution)
```

**Rôle :** Retourne une copie de la solution (liste de directions) pour éviter les mutations accidentelles.

**Exemple de retour :** `["E", "E", "S", "E", "N", ...]`

Chaque élément est une direction : `"N"` (Nord), `"S"` (Sud), `"E"` (Est), `"W"` (Ouest).

---

## `to_hex_lines` — Sérialisation hexadécimale

```python
def to_hex_lines(self) -> list[str]:
    return ["".join(f"{cell:X}" for cell in row) for row in self.grid]
```

**Rôle :** Convertit la grille en lignes de texte hexadécimal pour la sauvegarde. Chaque cellule (valeur 0-15) est convertie en un caractère hexadécimal (0-F).

**Exemple :** Une grille 2×2 :
```python
grid = [[7, 13], [11, 14]]
# 7 → '7', 13 → 'D', 11 → 'B', 14 → 'E'
# Résultat : ["7D", "BE"]
```

---

## Exemple complet

```python
from mazegen import MazeGenerator

# Création d'un labyrinthe 10×10 avec entrée (0,0) et sortie (9,9)
maze = MazeGenerator(
    width=10,
    height=10,
    entry=(0, 0),
    exit=(9, 9),
    seed=42  # graine fixe pour reproductibilité
)

# Génération
maze.generate()

# Vérifier un mur
print(maze.has_wall(0, 0, MazeGenerator.EAST))  # True ou False

# Obtenir la solution
solution = maze.get_solution()
print(solution)  # ex: ["E", "E", "S", "S", ...]

# Sérialisation hex
for line in maze.to_hex_lines():
    print(line)
```

---

## Schéma récapitulatif

```
MazeGenerator
│
├── __init__(width, height, entry, exit, seed)
│
├── generate()
│     ├── _init_grid()         → grille = [[15, 15, ...], ...]
│     ├── _carve_pattern42()   → marque les cellules du motif "42"
│     ├── _generate_dfs()      → creuse les passages
│     │     └── stack = [entry]
│     │           ├── voisins disponibles ? → random, remove_wall, push
│     │           └── plus de voisins ? → pop (backtrack)
│     ├── _solve_bfs()         → trouve le plus court chemin
│     │     └── queue = [entry]
│     │           ├── destination atteinte ? → reconstruit chemin
│     │           ├── voisin accessible ? → enqueue, parent[direction]
│     │           └── queue vide ? → pas de chemin
│     └── _generated = True
│
├── has_wall(x, y, direction)  → test bitmask
├── get_solution()             → liste ["N", "E", ...]
├── get_cell(x, y)             → valeur entière 0-15
├── to_hex_lines()             → ["F0A1", "37BC", ...]
└── to_hex_lines()
```

---

## Constantes utiles

| Nom | Valeur | Binaire |
|-----|--------|---------|
| `NORTH` | 1 | `0001` |
| `EAST` | 2 | `0010` |
| `SOUTH` | 4 | `0100` |
| `WEST` | 8 | `1000` |

`OPPOSITE` : dictionnaire de correspondance :
```python
OPPOSITE = {
    NORTH: SOUTH,  # 1 → 4
    SOUTH: NORTH,  # 4 → 1
    EAST: WEST,    # 2 → 8
    WEST: EAST,    # 8 → 2
}
```

`DELTA` : déplacement en pixels pour chaque direction :
```python
DELTA = {
    NORTH: (0, -1),   # déplacement vers le haut
    EAST:  (1, 0),    # déplacement vers la droite
    SOUTH: (0, 1),    # déplacement vers le bas
    WEST:  (-1, 0),   # déplacement vers la gauche
}
```
