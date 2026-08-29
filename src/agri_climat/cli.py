"""Point d'entrée en ligne de commande : pipeline jusqu'au ML basique."""

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
    download_nuts_provinces,
    download_rendements,
    rendements_raw_path,
)
from agri_climat.data.join import join_processed_files
from agri_climat.paths import docs_dir, processed_dir, raw_dir

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
    if kind in {"nuts", "all"}:
        download_nuts_provinces(raw, processed_dir())


def _cmd_clean(kind: str) -> None:
    raw = raw_dir()
    processed = processed_dir()
    if kind in {"rendements", "all"}:
        clean_rendements_file(rendements_raw_path(raw), processed)
    if kind in {"climat", "all"}:
        clean_climat_files(raw, processed)


def _cmd_join() -> None:
    join_processed_files(processed_dir(), docs_dir())


def _cmd_eda() -> None:
    from agri_climat.eda_preview import run_eda_preview

    run_eda_preview()


def _cmd_analyse() -> None:
    from agri_climat.analyse import run_analyse

    run_analyse()


def _cmd_figures() -> None:
    from agri_climat.figures import run_figures

    run_figures()


def _cmd_map() -> None:
    from agri_climat.map import run_map

    run_map()


def _cmd_ml() -> None:
    from agri_climat.ml import run_ml

    run_ml()


def build_parser() -> argparse.ArgumentParser:
    """Construit le parseur CLI."""
    parser = argparse.ArgumentParser(
        description="Pipeline agriculture-climat Wallonie (download, clean, join, analyse, figures, map, ml).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    download = sub.add_parser("download", help="Télécharger les fichiers bruts.")
    download.add_argument(
        "kind",
        nargs="?",
        default="all",
        choices=["all", "rendements", "climat", "nuts"],
    )

    clean = sub.add_parser("clean", help="Nettoyer les fichiers déjà téléchargés.")
    clean.add_argument(
        "kind",
        nargs="?",
        default="all",
        choices=["all", "rendements", "climat"],
    )

    sub.add_parser(
        "join",
        help="Joindre rendements et climat, écrire CSV/Parquet et docs/eda.md.",
    )
    sub.add_parser(
        "eda",
        help="Aperçu EDA dans le terminal + PNG (sans fenêtre graphique).",
    )
    sub.add_parser(
        "analyse",
        help="Corrélations, années atypiques, zoom froment (rapport + PNG).",
    )
    sub.add_parser(
        "figures",
        help="PNG polies pour le README (ranking, nuages, années à risque).",
    )
    sub.add_parser(
        "map",
        help="Choroplèthe provinciale froment (PNG README + GeoJSON).",
    )
    sub.add_parser(
        "ml",
        help="Baseline linéaire leave-one-year-out (rapport + PNG).",
    )
    sub.add_parser(
        "run",
        help="Télécharger, nettoyer, joindre, analyser, figures, carte, puis ML.",
    )
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
        elif args.command == "join":
            _cmd_join()
        elif args.command == "eda":
            _cmd_eda()
        elif args.command == "analyse":
            _cmd_analyse()
        elif args.command == "figures":
            _cmd_figures()
        elif args.command == "map":
            _cmd_map()
        elif args.command == "ml":
            _cmd_ml()
        elif args.command == "run":
            _cmd_download("all")
            _cmd_clean("all")
            _cmd_join()
            _cmd_analyse()
            _cmd_figures()
            _cmd_map()
            _cmd_ml()
    except FileNotFoundError as exc:
        logger.error("%s — lancer d'abord : python -m agri_climat clean (ou run)", exc)
        return 1
    except requests.RequestException as exc:
        logger.error("Échec du téléchargement : %s", exc)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
