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
