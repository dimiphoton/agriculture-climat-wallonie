"""Chemins du dépôt (données brutes et traitées)."""

from pathlib import Path


def repo_root() -> Path:
    """Retourne la racine du dépôt (parent de ``src/``)."""
    return Path(__file__).resolve().parents[2]


def raw_dir() -> Path:
    """Dossier des fichiers téléchargés, jamais modifiés après coup."""
    return repo_root() / "data" / "raw"


def processed_dir() -> Path:
    """Dossier des tables nettoyées, régénérables depuis ``data/raw``."""
    return repo_root() / "data" / "processed"


def docs_dir() -> Path:
    """Dossier de documentation du dépôt (EDA, décisions, présentations)."""
    return repo_root() / "docs"


def pictures_experiments_dir() -> Path:
    """Graphiques d'analyse (pas les figures polies du README)."""
    return repo_root() / "pictures" / "experiments"


def pictures_readme_dir() -> Path:
    """Figures polies destinées au README (libellés anglais)."""
    return repo_root() / "pictures" / "readme"


def sql_dir() -> Path:
    """Scripts SQL versionnés (schéma DuckDB et requêtes de croisement)."""
    return repo_root() / "sql"


def pictures_presentations_dir() -> Path:
    """Figures des slides, sous ``docs/`` pour que GitHub Pages les serve.

    ``docs/presentations/`` et ``docs/slides/`` sont au même niveau : le
    chemin Markdown ``../pictures/presentations/foo.png`` marche dans les
    deux dossiers. Un ``../../pictures/`` à la racine du repo est invisible
    sur Pages (seul ``/docs`` est publié).
    """
    return docs_dir() / "pictures" / "presentations"
