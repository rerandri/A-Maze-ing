# NOTE [PARSING]

# config_reader.py — Parseur brut (lecture fichier → dict)
   ## - Entrée : un TextIO (fichier ouvert ou io.StringIO)
   ## - Sortie : dict[str, object] non validé
   ## - Rôle : lit ligne par ligne, ignore les # et lignes vides, convertit les valeurs en types Python simples
   ## - Connaît la syntaxe : KEY=VALUE, coordonnées x,y, booléens true/false, SEED=none
   ## read_config_file(f)  →  {"WIDTH": 30, "PERFECT": True, "OUTPUT_FILE": "maze.txt"}
   ## C'est un parseur générique : il accepte n'importe quelle clé, même inconnue (return key, value ligne 32).


# config_parser.py — Validateur (dict → MazeConfig typé)
   ## - Entrée : un Mapping[str, object] (vient généralement de read_config_file)
   ## - Sortie : MazeConfig (TypedDict) normalisé et validé
   ## - Rôle : vérifie types, bornes, cohérence, ajoute les valeurs par défaut
   ## - Connaît le domaine métier :
   ## - WIDTH/HEIGHT ≥ 10
   ## - ENTRY/EXIT dans les limites + différents
   ## - PERFECT par défaut à True
   ## - OUTPUT_FILE par défaut à "output_maze.txt"
   ## - ENTRY par défaut (0, 0), EXIT par défaut (largeur-1, hauteur-1)parse_config({"WIDTH": 30})  
** → ValueError: Missing required configuration key: HEIGHT **
