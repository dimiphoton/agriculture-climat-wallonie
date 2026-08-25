"""Téléchargement des sources (Eurostat rendements, Open-Meteo climat)."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from urllib.parse import quote

import truststore

# Magasin de certificats de l'OS : sous Windows, certifi seul échoue souvent
# derrière un proxy d'entreprise.
truststore.inject_into_ssl()

import requests  # noqa: E402

from agri_climat.settings import (
    CLIMATE_POINTS,
    CROP_LABELS_FR,
    END_YEAR,
    EUROSTAT_DATASET,
    EUROSTAT_SDMX_URL,
    GEO_LABELS_FR,
    HTTP_TIMEOUT_S,
    HTTP_USER_AGENT,
    OPEN_METEO_ARCHIVE_URL,
    OPEN_METEO_DAILY_VARS,
    START_YEAR,
)

logger = logging.getLogger(__name__)

_HEADERS = {"User-Agent": HTTP_USER_AGENT, "Accept": "*/*"}
_RETRY_PAUSES_S = (0, 5, 20, 45)


def _get_with_retry(
    url: str,
    params: dict[str, object] | None = None,
) -> requests.Response:
    """GET avec pauses si l'API répond 429 (quota Open-Meteo)."""
    response: requests.Response | None = None
    for attempt, pause in enumerate(_RETRY_PAUSES_S, start=1):
        if pause:
            logger.info("Pause %s s avant nouvel essai (%s/%s)", pause, attempt, len(_RETRY_PAUSES_S))
            time.sleep(pause)
        response = requests.get(
            url,
            params=params,
            headers=_HEADERS,
            timeout=HTTP_TIMEOUT_S,
        )
        if response.status_code != 429:
            response.raise_for_status()
            return response
        logger.warning("HTTP 429 Too Many Requests")
    assert response is not None
    response.raise_for_status()
    return response


def rendements_raw_path(raw_root: Path) -> Path:
    """Chemin du TSV Eurostat brut."""
    return raw_root / "eurostat_apro_cpshr_wallonie.tsv"


def climat_raw_path(raw_root: Path, geo_code: str) -> Path:
    """Chemin du JSON Open-Meteo brut pour un point."""
    return raw_root / f"openmeteo_{geo_code}.json"


def download_rendements(raw_root: Path) -> Path:
    """Télécharge les rendements régionaux Eurostat (NUTS 1-2 wallons).

    Parameters
    ----------
    raw_root
        Dossier ``data/raw``.

    Returns
    -------
    Path
        Fichier TSV enregistré.

    Raises
    ------
    requests.HTTPError
        Si l'API Eurostat répond une erreur HTTP.
    """
    raw_root.mkdir(parents=True, exist_ok=True)
    crops = "+".join(CROP_LABELS_FR)
    geos = "+".join(GEO_LABELS_FR)
    key = f"A.{crops}.AR_THS_HA+HPRD_HUMD_EU_THS_T.{geos}"
    url = EUROSTAT_SDMX_URL.format(
        dataset=EUROSTAT_DATASET,
        key=quote(key, safe=".+"),
    )
    logger.info("Téléchargement Eurostat %s", url)
    response = _get_with_retry(url)
    target = rendements_raw_path(raw_root)
    target.write_text(response.text, encoding="utf-8")
    logger.info("Écrit %s (%s octets)", target, target.stat().st_size)
    return target


def download_climat(raw_root: Path) -> list[Path]:
    """Télécharge les séries quotidiennes Open-Meteo (ERA5) par province.

    Parameters
    ----------
    raw_root
        Dossier ``data/raw``.

    Returns
    -------
    list of Path
        Un JSON par point climatique.

    Raises
    ------
    requests.HTTPError
        Si l'API Open-Meteo répond une erreur HTTP.
    """
    raw_root.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    start = f"{START_YEAR}-01-01"
    end = f"{END_YEAR}-12-31"
    for point in CLIMATE_POINTS:
        target = climat_raw_path(raw_root, point.code)
        if target.exists():
            logger.info("Déjà présent, on saute %s", target.name)
            written.append(target)
            continue
        params = {
            "latitude": point.latitude,
            "longitude": point.longitude,
            "start_date": start,
            "end_date": end,
            "daily": ",".join(OPEN_METEO_DAILY_VARS),
            "timezone": "Europe/Brussels",
        }
        logger.info("Téléchargement Open-Meteo %s (%s)", point.code, point.label)
        response = _get_with_retry(OPEN_METEO_ARCHIVE_URL, params=params)
        payload = response.json()
        payload["geo_code"] = point.code
        payload["geo_label"] = point.label
        target.write_text(
            json.dumps(payload, ensure_ascii=False),
            encoding="utf-8",
        )
        logger.info("Écrit %s", target)
        written.append(target)
        time.sleep(2)
    return written
