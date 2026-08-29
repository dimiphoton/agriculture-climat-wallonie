"""Tests de l'entrepôt DuckDB (schéma, agrégats SQL, requêtes)."""

from pathlib import Path

import pandas as pd

from agri_climat.data.clean_climat import daily_to_monthly, monthly_to_annual
from agri_climat.data.warehouse import build_warehouse, run_queries
from agri_climat.paths import sql_dir
from tests.test_clean_climat import _daily_fixture
from tests.test_join import _rendements


def _daily_csv_rows() -> pd.DataFrame:
    """Quelques jours 2020–2021, deux provinces (Wallonie = moyenne SQL)."""
    rows: list[dict[str, object]] = []
    for year, month, day, t_hainaut, t_namur, p_hainaut, p_namur in [
        (2020, 1, 15, 2.0, 4.0, 1.0, 3.0),
        (2020, 6, 15, 18.0, 20.0, 4.0, 6.0),
        (2020, 6, 20, 26.0, 28.0, 12.0, 0.0),  # jour chaud + jour arrosé / sec
        (2021, 6, 15, 19.0, 21.0, 5.0, 7.0),
    ]:
        rows.append(
            {
                "date": f"{year}-{month:02d}-{day:02d}",
                "geo": "BE32",
                "geo_label": "Hainaut",
                "temp_mean_c": t_hainaut,
                "temp_max_c": t_hainaut + 5,
                "precip_mm": p_hainaut,
                "et0_mm": 2.0,
            }
        )
        rows.append(
            {
                "date": f"{year}-{month:02d}-{day:02d}",
                "geo": "BE35",
                "geo_label": "Namur",
                "temp_mean_c": t_namur,
                "temp_max_c": t_namur + 5,
                "precip_mm": p_namur,
                "et0_mm": 2.5,
            }
        )
    return pd.DataFrame(rows)


def _write_native_csvs(processed: Path) -> None:
    """Écrit rendements + climat quotidien pour build_warehouse."""
    processed.mkdir(parents=True, exist_ok=True)
    _rendements().to_csv(processed / "rendements.csv", index=False)
    _daily_csv_rows().to_csv(processed / "climat_quotidien.csv", index=False)


def test_sql_annuel_somme_precip_et_saison(tmp_path: Path) -> None:
    """Même règle qu'en pandas : pluie sommée, saison = juin ici."""
    _write_native_csvs(tmp_path)
    joined = build_warehouse(tmp_path)
    hainaut_2020 = joined[
        (joined["geo"] == "BE32")
        & (joined["year"] == 2020)
        & (joined["crop_code"] == "C1110")
    ].iloc[0]
    # 1 (jan) + 4 + 12 (juin)
    assert hainaut_2020["precip_mm"] == 17.0
    assert hainaut_2020["precip_growing_mm"] == 16.0
    # Tmax Hainaut 18+5=23 et 26+5=31 → un jour >= 25 °C en saison
    assert hainaut_2020["n_hot_days_growing"] == 1
    assert hainaut_2020["n_wet_days_growing"] == 1  # 12 mm
    assert hainaut_2020["n_dry_days_growing"] == 0  # 4 et 12 mm, pas de jour < 1


def test_sql_wallonie_moyenne_provinces(tmp_path: Path) -> None:
    """BE3 n'est pas dans le fait journalier : la vue fait la moyenne."""
    _write_native_csvs(tmp_path)
    joined = build_warehouse(tmp_path)
    wallonie = joined[
        (joined["geo"] == "BE3")
        & (joined["year"] == 2020)
        & (joined["crop_code"] == "C1110")
    ].iloc[0]
    # Provinces 2020 : precip 17 et 3+6+0=9 → moyenne 13
    assert wallonie["precip_mm"] == 13.0


def test_sql_inner_join_ecarte_annee_orpheline(tmp_path: Path) -> None:
    """2022 a des rendements, pas de climat → absente."""
    _write_native_csvs(tmp_path)
    joined = build_warehouse(tmp_path)
    assert set(joined["year"].unique()) == {2020, 2021}
    assert (tmp_path / "agri_climat.duckdb").exists()
    assert (tmp_path / "rendements_climat.parquet").exists()


def test_sql_agregat_aligne_pandas() -> None:
    """La formule mensuelle SQL = daily_to_monthly (oracle pandas)."""
    daily = _daily_fixture()
    pandas_monthly = daily_to_monthly(daily)
    hainaut = pandas_monthly[
        (pandas_monthly["geo"] == "BE32") & (pandas_monthly["month"] == 6)
    ].iloc[0]
    assert hainaut["precip_mm"] == 4.0
    pandas_annual = monthly_to_annual(pandas_monthly)
    assert pandas_annual[pandas_annual["geo"] == "BE32"].iloc[0]["precip_mm"] == 5.0


def test_queries_sql_s_executent(tmp_path: Path) -> None:
    """Les 8 SELECT de queries.sql tournent sur une petite base."""
    _write_native_csvs(tmp_path)
    build_warehouse(tmp_path)
    frames = run_queries(tmp_path, sql_dir() / "queries.sql")
    assert len(frames) == 8
    # Requête 7 : indice par culture, au moins le froment wallon
    risk = frames[6]
    assert "indice_risque_moyen" in risk.columns
