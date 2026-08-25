"""Point d'entrée en ligne de commande : téléchargement et nettoyage."""

from __future__ import annotations

import argparse
import logging
import sys

import truststore

truststore.inject_into_ssl()

import requests  # noqa: E402

from agri_climat.data.clean_climat import clean_climat_files
from agri_climat.data.clean_rendements import clean_rendements_file
from agri_climat.data.download import (
    download_climat,
    download_rendements,
    rendements_raw_path,
)
from agri_climat.paths import processed_dir, raw_dir

logger = logging.getLogger(__name__)


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )


def _cmd_download(kind: str) -> None:
    raw = raw_dir()
    if kind in {"rendements", "all"}:
        download_rendements(raw)
    if kind in {"climat", "all"}:
        download_climat(raw)


def _cmd_clean(kind: str) -> None:
    raw = raw_dir()
    processed = processed_dir()
    if kind in {"rendements", "all"}:
        clean_rendements_file(rendements_raw_path(raw), processed)
    if kind in {"climat", "all"}:
        clean_climat_files(raw, processed)


def build_parser() -> argparse.ArgumentParser:
    """Construit le parseur CLI."""
    parser = argparse.ArgumentParser(
        description="Acquisition et nettoyage des données agriculture-climat Wallonie.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    download = sub.add_parser("download", help="Télécharger les fichiers bruts.")
    download.add_argument(
        "kind",
        nargs="?",
        default="all",
        choices=["all", "rendements", "climat"],
    )

    clean = sub.add_parser("clean", help="Nettoyer les fichiers déjà téléchargés.")
    clean.add_argument(
        "kind",
        nargs="?",
        default="all",
        choices=["all", "rendements", "climat"],
    )

    sub.add_parser("run", help="Télécharger puis nettoyer (pipeline complet).")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Point d'entrée principal du CLI.

    Parameters
    ----------
    argv
        Arguments CLI ; ``None`` lit ``sys.argv``.

    Returns
    -------
    int
        Code de sortie (0 = succès).
    """
    _configure_logging()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "download":
            _cmd_download(args.kind)
        elif args.command == "clean":
            _cmd_clean(args.kind)
        elif args.command == "run":
            _cmd_download("all")
            _cmd_clean("all")
    except FileNotFoundError as exc:
        logger.error("%s — lancer d'abord : python -m agri_climat download", exc)
        return 1
    except requests.RequestException as exc:
        logger.error("Échec du téléchargement : %s", exc)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
