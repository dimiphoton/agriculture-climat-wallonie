"""Entrepôt DuckDB : charge les grains natifs et calcule les vues SQL."""

from __future__ import annotations

import logging
from pathlib import Path

import duckdb
import pandas as pd

from agri_climat.paths import sql_dir

logger = logging.getLogger(__name__)

DB_NAME = "agri_climat.duckdb"


def duckdb_path(processed_root: Path) -> Path:
    """Chemin du fichier DuckDB régénérable."""
    return processed_root / DB_NAME


def execute_sql_script(con: duckdb.DuckDBPyConnection, sql: str) -> None:
    """Exécute un script SQL (plusieurs instructions, commentaires compris)."""
    statements = duckdb.extract_statements(sql)
    for statement in statements:
        con.execute(statement.query)


def _remove_existing_db(db_path: Path) -> None:
    """Supprime le fichier DuckDB et son WAL pour un rebuild propre."""
    wal_path = Path(str(db_path) + ".wal")
    for path in (db_path, wal_path):
        if path.exists():
            path.unlink()


def _csv_literal(path: Path) -> str:
    """Chemin POSIX quoté pour read_csv_auto (Windows inclus)."""
    return path.resolve().as_posix().replace("'", "''")


def _load_tables(
    con: duckdb.DuckDBPyConnection,
    rendements_csv: Path,
    climat_quotidien_csv: Path,
) -> None:
    """Remplit dimensions et faits depuis les CSV au grain natif."""
    rend = _csv_literal(rendements_csv)
    daily = _csv_literal(climat_quotidien_csv)

    con.execute(
        f"""
        INSERT INTO dim_culture
        SELECT DISTINCT crop_code, crop_label
        FROM read_csv_auto('{rend}')
        """
    )
    con.execute(
        f"""
        INSERT INTO dim_territoire
        SELECT geo, geo_label, nuts_level
        FROM (
            SELECT
                geo,
                geo_label,
                CASE WHEN geo = 'BE3' THEN 'nuts1' ELSE 'nuts2' END AS nuts_level
            FROM read_csv_auto('{rend}')
            UNION
            SELECT
                geo,
                geo_label,
                CASE WHEN geo = 'BE3' THEN 'nuts1' ELSE 'nuts2' END AS nuts_level
            FROM read_csv_auto('{daily}')
        )
        """
    )
    con.execute(
        f"""
        INSERT INTO dim_annee
        SELECT DISTINCT year
        FROM (
            SELECT CAST(year AS INTEGER) AS year
            FROM read_csv_auto('{rend}')
            UNION
            SELECT CAST(year(CAST(date AS DATE)) AS INTEGER) AS year
            FROM read_csv_auto('{daily}')
        )
        """
    )
    con.execute(
        f"""
        INSERT INTO fact_rendements
        SELECT
            CAST(year AS INTEGER),
            geo,
            crop_code,
            area_kha,
            production_kt,
            yield_t_ha,
            imputed
        FROM read_csv_auto('{rend}')
        """
    )
    con.execute(
        f"""
        INSERT INTO fact_climat_quotidien
        SELECT
            CAST(date AS DATE),
            geo,
            temp_mean_c,
            temp_max_c,
            precip_mm,
            et0_mm
        FROM read_csv_auto('{daily}')
        WHERE geo != 'BE3'
        """
    )


def _export_views(con: duckdb.DuckDBPyConnection, processed_root: Path) -> pd.DataFrame:
    """Écrit les CSV / Parquet dérivés des vues (même schéma qu'avant + seuils)."""
    monthly = con.execute(
        "SELECT * FROM v_climat_mensuel ORDER BY geo, year, month"
    ).df()
    annual = con.execute(
        "SELECT * FROM v_climat_annuel ORDER BY geo, year"
    ).df()
    joined = con.execute(
        "SELECT * FROM v_rendements_climat ORDER BY crop_code, geo, year"
    ).df()

    monthly.to_csv(processed_root / "climat_mensuel.csv", index=False)
    annual.to_csv(processed_root / "climat_annuel.csv", index=False)
    joined.to_csv(processed_root / "rendements_climat.csv", index=False)
    joined.to_parquet(processed_root / "rendements_climat.parquet", index=False)
    logger.info("Écrit climat_mensuel.csv (%s lignes)", len(monthly))
    logger.info("Écrit climat_annuel.csv (%s lignes)", len(annual))
    logger.info("Écrit rendements_climat.csv (%s lignes)", len(joined))
    return joined


def build_warehouse(
    processed_root: Path,
    schema_path: Path | None = None,
) -> pd.DataFrame:
    """Crée la base DuckDB à partir des CSV natifs et exporte les vues.

    Parameters
    ----------
    processed_root
        Dossier ``data/processed`` (rendements.csv + climat_quotidien.csv).
    schema_path
        ``sql/schema.sql`` du dépôt, sauf surcharge (tests).

    Returns
    -------
    pandas.DataFrame
        Contenu de ``v_rendements_climat``.

    Raises
    ------
    FileNotFoundError
        Si un CSV natif est absent.
    """
    rend_path = processed_root / "rendements.csv"
    daily_path = processed_root / "climat_quotidien.csv"
    if not rend_path.exists():
        raise FileNotFoundError(rend_path)
    if not daily_path.exists():
        raise FileNotFoundError(daily_path)

    schema_file = schema_path or (sql_dir() / "schema.sql")
    schema_sql = schema_file.read_text(encoding="utf-8")

    processed_root.mkdir(parents=True, exist_ok=True)
    db_path = duckdb_path(processed_root)
    _remove_existing_db(db_path)

    con = duckdb.connect(str(db_path))
    try:
        execute_sql_script(con, schema_sql)
        _load_tables(con, rend_path, daily_path)
        joined = _export_views(con, processed_root)
        logger.info("Base DuckDB : %s", db_path)
        return joined
    finally:
        con.close()


def connect_warehouse(processed_root: Path) -> duckdb.DuckDBPyConnection:
    """Ouvre la base déjà construite (lecture)."""
    db_path = duckdb_path(processed_root)
    if not db_path.exists():
        raise FileNotFoundError(db_path)
    return duckdb.connect(str(db_path), read_only=True)


def run_queries(
    processed_root: Path,
    queries_path: Path | None = None,
) -> list[pd.DataFrame]:
    """Exécute ``sql/queries.sql`` et retourne un DataFrame par SELECT."""
    sql_file = queries_path or (sql_dir() / "queries.sql")
    sql = sql_file.read_text(encoding="utf-8")
    con = connect_warehouse(processed_root)
    try:
        results: list[pd.DataFrame] = []
        for statement in duckdb.extract_statements(sql):
            frame = con.execute(statement.query).df()
            results.append(frame)
        return results
    finally:
        con.close()
