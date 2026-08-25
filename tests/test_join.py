"""Tests de la jointure rendements × climat et des anomalies."""

import pandas as pd

from agri_climat.data.join import (
    add_climate_anomalies,
    build_eda_markdown,
    join_rendements_climat,
)


def _rendements() -> pd.DataFrame:
    """Deux cultures, deux territoires, années 2020–2021 (+ 2022 orpheline)."""
    rows = []
    for year in (2020, 2021, 2022):
        rows.append(
            {
                "year": year,
                "geo": "BE3",
                "geo_label": "Wallonie",
                "crop_code": "C1110",
                "crop_label": "Froment et épeautre",
                "area_kha": 140.0,
                "production_kt": 1120.0,
                "yield_t_ha": 8.0,
                "imputed": year == 2021,
            }
        )
        rows.append(
            {
                "year": year,
                "geo": "BE32",
                "geo_label": "Hainaut",
                "crop_code": "C1110",
                "crop_label": "Froment et épeautre",
                "area_kha": 50.0,
                "production_kt": 400.0,
                "yield_t_ha": 8.0,
                "imputed": False,
            }
        )
    rows.append(
        {
            "year": 2020,
            "geo": "BE3",
            "geo_label": "Wallonie",
            "crop_code": "R2000",
            "crop_label": "Betterave sucrière",
            "area_kha": 20.0,
            "production_kt": 1600.0,
            "yield_t_ha": 80.0,
            "imputed": False,
        }
    )
    return pd.DataFrame(rows)


def _climat() -> pd.DataFrame:
    """Climat 2020–2021 seulement (2022 rendements sans climat → inner drop)."""
    return pd.DataFrame(
        [
            {
                "geo": "BE3",
                "geo_label": "Wallonie",
                "year": 2020,
                "temp_mean_c": 10.0,
                "precip_mm": 800.0,
                "et0_mm": 600.0,
                "temp_mean_growing_c": 16.0,
                "precip_growing_mm": 400.0,
                "et0_growing_mm": 500.0,
            },
            {
                "geo": "BE3",
                "geo_label": "Wallonie",
                "year": 2021,
                "temp_mean_c": 12.0,
                "precip_mm": 700.0,
                "et0_mm": 650.0,
                "temp_mean_growing_c": 18.0,
                "precip_growing_mm": 300.0,
                "et0_growing_mm": 550.0,
            },
            {
                "geo": "BE32",
                "geo_label": "Hainaut",
                "year": 2020,
                "temp_mean_c": 11.0,
                "precip_mm": 750.0,
                "et0_mm": 610.0,
                "temp_mean_growing_c": 17.0,
                "precip_growing_mm": 380.0,
                "et0_growing_mm": 510.0,
            },
            {
                "geo": "BE32",
                "geo_label": "Hainaut",
                "year": 2021,
                "temp_mean_c": 11.0,
                "precip_mm": 750.0,
                "et0_mm": 610.0,
                "temp_mean_growing_c": 17.0,
                "precip_growing_mm": 380.0,
                "et0_growing_mm": 510.0,
            },
        ]
    )


def test_anomalies_somme_nulle_par_geo() -> None:
    """Sur deux années, les anomalies d'un geo s'annulent."""
    with_anom = add_climate_anomalies(_climat())
    wallonie = with_anom[with_anom["geo"] == "BE3"]
    assert abs(wallonie["temp_mean_c_anom"].sum()) < 1e-9
    assert wallonie["temp_mean_c_anom"].tolist() == [-1.0, 1.0]


def test_zscore_nul_si_ecart_type_nul() -> None:
    """Hainaut identique les deux années → z-score indéfini."""
    with_anom = add_climate_anomalies(_climat())
    hainaut = with_anom[with_anom["geo"] == "BE32"]
    assert hainaut["precip_mm_anom"].eq(0).all()
    assert hainaut["precip_mm_z"].isna().all()


def test_jointure_interne_ecarte_annee_orpheline() -> None:
    """2022 n'a pas de climat → absente de la table consolidée."""
    joined = join_rendements_climat(_rendements(), _climat())
    assert set(joined["year"].unique()) == {2020, 2021}
    # 2 geos × 2 années × froment + 1 betterave 2020 = 5
    assert len(joined) == 5
    be3_2020 = joined[
        (joined["geo"] == "BE3")
        & (joined["year"] == 2020)
        & (joined["crop_code"] == "C1110")
    ].iloc[0]
    assert be3_2020["precip_growing_mm"] == 400.0
    assert be3_2020["temp_mean_c_anom"] == -1.0


def test_rapport_eda_contient_limites() -> None:
    """Le markdown d'EDA mentionne la couverture et les garde-fous."""
    joined = join_rendements_climat(_rendements(), _climat())
    text = build_eda_markdown(joined)
    assert "Froment et épeautre" in text
    assert "imputées" in text
    assert "CMIP6" in text
    assert "Corrélation ≠ causalité" in text


def test_export_csv_et_parquet(tmp_path) -> None:
    """join_processed_files écrit les deux formats et un eda.md."""
    from agri_climat.data.join import join_processed_files

    processed = tmp_path / "processed"
    docs = tmp_path / "docs"
    processed.mkdir()
    _rendements().to_csv(processed / "rendements.csv", index=False)
    _climat().to_csv(processed / "climat_annuel.csv", index=False)

    csv_path = join_processed_files(processed, docs)
    parquet_path = processed / "rendements_climat.parquet"
    assert csv_path.exists()
    assert parquet_path.exists()
    roundtrip = pd.read_parquet(parquet_path)
    assert len(roundtrip) == 5
    assert (docs / "eda.md").exists()
