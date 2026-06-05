# Explication détaillée du MlxRenderer

## Aperçu général

`MlxRenderer` est le rendu graphique du labyrinthe utilisant la bibliothèque **MiniLibX** (librairie graphique de 42). Elle permet d'afficher le labyrinthe dans une fenêtre avec des animations et des interactions clavier, contrairement au `AsciiRenderer` qui fonctionne uniquement en terminal.

Le fichier `mlx.py` est un **wrapper Python** de la bibliothèque C `libmlx.so` via `ctypes`. Tous les appels MLX (création fenêtre, image, boucle d'événements) passent par ce wrapper.

---

## Palette de couleurs — `MlxColor`

```python
class MlxColor:
    WALL_WHITE: int = 0xFF_E8E8E8
    WALL_CYAN: int = 0xFF_00C8C8
    WALL_PURPLE: int = 0xFF_9B59B6
    BACKGROUND: int = 0xFF_1A1A2E
    BLOCKED: int = 0xFF_6C3483
    PATH: int = 0xFF_2ECC71
    START: int = 0xFF_3498DB
    END: int = 0xFF_E74C3C
```

Chaque couleur est un entier 32 bits au format **ARGB** (Alpha, Rouge, Vert, Bleu). Le préfixe `0xFF_` signifie une opacité totale. Par exemple :
- `0xFF_E8E8E8` → blanc clair opaque (murs par défaut)
- `0xFF_1A1A2E` → bleu foncé presque noir (fond de la cellule)

---

## `__init__` — Constructeur

```python
def __init__(self, maze: MazeGenerator, cell_size: int = 20) -> None:
```

**Rôle :** Initialise le renderer avec le labyrinthe généré et la taille des cellules en pixels.

**Paramètres :**
- `maze` — une instance de `MazeGenerator` déjà générée (`maze.generate()` appelé)
- `cell_size` — taille en pixels d'une cellule (ex: 20 px). Les murs faisant 1 cellule de large, un mur fait aussi 20 px.

**Attributs importants :**
- `_color_index` — index de la couleur actuelle des murs (pour le cycle de couleurs)
- `_show_path` — booléen pour afficher/cacher le chemin solution
- `_path_step` — compteur d'avancement dans l'animation du chemin
- `_solution` — copie de `maze.get_solution()` : liste de chaînes `"N"`, `"S"`, `"E"`, `"W"`
- `_animating` — booléen qui contrôle la boucle d'animation
- `_mlx`, `_mlx_ptr`, `_win_ptr`, `_img_ptr`, `_img_data`, `_img_sl` — pointeurs et ressources MLX

**Exemple :**
```python
maze = MazeGenerator(width=20, height=20, entry=(0,0), exit=(19,19))
maze.generate()
renderer = MlxRenderer(maze, cell_size=24)
renderer.run()
```

---

## Propriétés géométriques

### `_win_width` et `_win_height`

```python
@property
def _win_width(self) -> int:
    return (self.maze.width * 2 + 1) * self.cell_size
```

**Logique :** Le labyrinthe est représenté par une grille de `(2*W+1) x (2*H+1)` cellules (chaque cellule du labyrinthe est encadrée par des murs). Chaque case de cette grille fait `cell_size` pixels.

**Exemple :** Pour un labyrinthe 20×20 avec `cell_size=20` :
- Largeur fenêtre = `(20*2 + 1) * 20 = 41 * 20 = 820 px`
- Hauteur fenêtre = idem : `(20*2 + 1) * 20 = 820 px`

---

## Affichage pixel — `_put_pixel`

```python
def _put_pixel(self, x: int, y: int, color: int) -> None:
    if self._img_data is None:
        return
    offset: int = y * self._img_sl + x * 4
    if offset + 3 >= len(self._img_data):
        return
    self._img_data[offset:offset + 4] = color.to_bytes(4, 'little')
```

**Rôle :** Écrit un pixel dans le buffer de l'image MLX.

**Logique :**
1. Vérifie que `_img_data` (un `memoryview`) n'est pas `None`
2. Calcule l'offset dans le buffer : `y * size_line + x * 4` (4 octets par pixel en ARGB)
3. Vérifie les bornes pour éviter les segfaults
4. Convertit l'entier ARGB en 4 octets (little-endian) et écrit dans le buffer

**Exemple :** Pour écrire un pixel rouge en (10, 20) :
```
offset = 20 * _img_sl + 10 * 4
# Écrit 0x44, 0x3C, 0xE7, 0xFF (ARGB de E74C3C) dans le buffer
```

---

## Remplissage de cellule — `_fill_cell`

```python
def _fill_cell(self, grid_x: int, grid_y: int, color: int) -> None:
    px: int = grid_x * self.cell_size
    py: int = grid_y * self.cell_size
    for dy in range(self.cell_size):
        for dx in range(self.cell_size):
            self._put_pixel(px + dx, py + dy, color)
```

**Rôle :** Remplit un carré de `cell_size × cell_size` pixels à la position `(grid_x, grid_y)` de la grille.

**Logique :** Boucle double sur les coordonnées locales `(dx, dy)` et appelle `_put_pixel` pour chaque pixel du carré.

**Exemple :** Avec `cell_size=20`, `_fill_cell(3, 5, MlxColor.BACKGROUND)` remplit un carré 20×20 allant du pixel (60, 100) au pixel (79, 119).

---

## Dessin du labyrinthe — `_draw_maze`

```python
def _draw_maze(self) -> None:
```

**Rôle :** Redessine intégralement le labyrinthe dans le buffer image.

**Logique :**
1. Remplit d'abord **toute** la grille avec la couleur des murs (blanc par défaut)
2. Ensuite, pour chaque cellule `(x, y)` du labyrinthe :
   - Si bloquée → couleur `BLOCKED` (violet), sinon → `BACKGROUND` (bleu foncé)
   - Pour chaque direction sans mur (vérifiée avec `maze.has_wall`), colore la case adjacente avec `BACKGROUND`
3. Enfin, colorie l'entrée (`START` — bleu) et la sortie (`END` — rouge)

**Exemple visuel** pour une cellule (1, 1) sans mur au Nord ni à l'Est :
```
Grille (3×3) de la cellule :
(2,0) mur  | (2,1) vide  | (2,2) mur
(1,0) vide | (1,1) fond  | (1,2) mur
(0,0) mur  | (0,1) mur   | (0,2) mur
```

---

## Animation du chemin — `_draw_path_step`

```python
def _draw_path_step(self) -> None:
```

**Rôle :** Avance l'animation du chemin solution d'un pas. Appelée à chaque frame par le hook de boucle MLX.

**Logique :**
1. Si tous les pas sont faits → remet la couleur `END` sur la sortie, arrête l'animation
2. Sinon, lit le mouvement courant : `"N"`, `"S"`, `"E"`, `"W"`
3. Colore la case correspondante en `PATH` (vert)
4. Incrémente `_path_step` et appelle `_flush()`

**Exemple :** Si la solution est `["E", "E", "S", "S"]` :
- Étape 0 : colorie la case à l'Est de l'entrée, `_curr_x += 1`
- Étape 1 : colorie la case à l'Est, `_curr_x += 1`
- Étape 2 : colorie la case au Sud, `_curr_y += 1`
- Étape 3 : colorie la case au Sud, `_curr_y += 1`, puis restaure la sortie

---

## Flush & Refresh

### `_flush`

```python
def _flush(self) -> None:
    if self._mlx and self._mlx_ptr and self._win_ptr and self._img_ptr:
        self._mlx.mlx_put_image_to_window(
            self._mlx_ptr, self._win_ptr, self._img_ptr, 0, 0
        )
```

**Rôle :** Pousse le buffer image vers la fenêtre (swap buffer). Sans cet appel, les modifications du buffer ne sont pas visibles.

### `_refresh`

```python
def _refresh(self) -> None:
    self._draw_maze()
    self._flush()
    if self._show_path:
        self._solution = self.maze.get_solution()
        ex, ey = self.maze.entry
        self._curr_x, self._curr_y = ex, ey
        self._path_step = 0
        self._animating = True
```

**Rôle :** Redessine le labyrinthe complet et relance l'animation si `_show_path` est actif.

---

## Gestion des événements clavier

### `_on_key`

```python
def _on_key(self, keycode: int, param: object) -> None:
```

**Rôle :** Callback appelé par MLX à chaque pression de touche.

| Touche | Code | Action |
|--------|------|--------|
| ESC | 65307 | Nettoie et quitte |
| R | 114 | Régénère un nouveau labyrinthe aléatoire |
| P | 112 | Bascule l'affichage du chemin |
| C | 99 | Cycle les couleurs des murs |

**Exemple** de régénération (touche R) :
```python
self.maze.seed = random.randint(0, 2**32)
self.maze.entry = (rand_x, rand_y)
self.maze.exit = (rand_x, rand_y)
self.maze._generated = False
self.maze.generate()
self._refresh()
```

---

## Boucle principale — `run`

```python
def run(self) -> None:
```

**Rôle :** Point d'entrée du renderer MLX. Crée la fenêtre, initialise l'image, enregistre les hooks et lance la boucle d'événements.

**Étapes :**
1. Crée l'instance MLX via `Mlx()`
2. Initialise la connexion avec `mlx_init()`
3. Crée la fenêtre avec `mlx_new_window()`
4. Crée le buffer image avec `mlx_new_image()`
5. Récupère l'adresse du buffer avec `mlx_get_data_addr()` → retourne `(memoryview, bpp, size_line, format)`
6. Enregistre les hooks :
   - `mlx_key_hook` → `_on_key`
   - `mlx_loop_hook` → `_on_loop` (animation)
   - `mlx_hook(win, 33, 0, ...)` → `_on_close` (événement WM_DELETE_WINDOW)
7. Dessine le labyrinthe avec `_refresh()`
8. Affiche les instructions dans le terminal
9. Lance `mlx_loop()` qui **bloque** jusqu'à la fermeture

**Exemple d'utilisation :**
```bash
python a_maze_ing.py config.txt
# Choisir "2. Graphical (MLX)" au prompt
```

---

## Nettoyage — `_cleanup`

```python
def _cleanup(self) -> None:
```

**Rôle :** Détruit les ressources MLX dans l'ordre correct pour éviter les fuites mémoire :
1. `mlx_destroy_image` → détruit l'image
2. `mlx_destroy_window` → détruit la fenêtre
3. `mlx_release` → libère la connexion MLX

---

## Résumé du pipeline d'affichage

```
run()
  ├── Initialisation MLX (connexion, fenêtre, image buffer)
  ├── Enregistrement des hooks (clavier, boucle, fermeture)
  ├── _refresh()
  │     ├── _draw_maze()
  │     │     ├── fond = couleur mur partout
  │     │     ├── pour chaque cellule : fond/path/blocked
  │     │     └── entrée (bleu) + sortie (rouge)
  │     ├── _flush()
  │     └── si show_path → initialise animation
  └── mlx_loop()  ← boucle infinie
        ├── _on_loop() (si _animating)
        │     └── _draw_path_step() → _flush()
        └── _on_key() (interactions)
              ├── R → regénère
              ├── P → toggle chemin
              ├── C → change couleur
              └── ESC → _cleanup() + exit
```
