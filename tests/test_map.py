"""Tests de la carte provinciale (GeoJSON de fixture, pas de GISCO)."""

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from agri_climat.analyse import add_yield_residuals
from agri_climat.data.download import filter_walloon_nuts, nuts_processed_path
from agri_climat.map import (
    README_MAP,
    plot_synthesis_map,
    run_map,
    wheat_precip_spearman_by_province,
    wheat_residual_by_province,
)
from tests.test_analyse import _joined_fixture


def _square_feature(nuts_id: str, x0: float, y0: float) -> dict:
    """Un carré GeoJSON (lon/lat fictifs) pour tests hors réseau."""
    return {
        "type": "Feature",
        "properties": {"NUTS_ID": nuts_id},
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [x0, y0],
                    [x0 + 1, y0],
                    [x0 + 1, y0 + 1],
                    [x0, y0 + 1],
                    [x0, y0],
                ]
            ],
        },
    }


def _fixture_geojson() -> dict:
    return {
        "type": "FeatureCollection",
        "features": [
            _square_feature("BE31", 4.0, 50.0),
            _square_feature("BE32", 5.0, 50.0),
        ],
    }


def test_filtre_garde_uniquement_les_provinces_wallonnes() -> None:
    """BE10 (Flandre) est écarté ; BE32 est conservé."""
    geojson = {
        "type": "FeatureCollection",
        "features": [
            _square_feature("BE10", 3.0, 51.0),
            _square_feature("BE32", 4.0, 50.0),
        ],
    }
    filtered = filter_walloon_nuts(geojson)
    ids = [feat["properties"]["NUTS_ID"] for feat in filtered["features"]]
    assert ids == ["BE32"]


def test_spearman_provincial_froment_pluie() -> None:
    """Le fixture lie le froment à la pluie : ρ positif en Hainaut."""
    table = add_yield_residuals(_joined_fixture())
    spearman = wheat_precip_spearman_by_province(table)
    hainaut = spearman[spearman["geo"] == "BE32"].iloc[0]
    assert hainaut["spearman_r"] > 0.95


def test_residu_annee_presente() -> None:
    """2010 existe dans le fixture : une ligne Hainaut."""
    table = add_yield_residuals(_joined_fixture())
    residual = wheat_residual_by_province(table, year=2010)
    assert "BE32" in set(residual["geo"])
    assert residual["yield_resid_z"].notna().all()


def test_carte_deux_panneaux_et_run(tmp_path) -> None:
    """PNG et CSV écrits sans appeler GISCO."""
    processed = tmp_path / "processed"
    figures = tmp_path / "readme"
    processed.mkdir()
    geo_path = nuts_processed_path(processed)
    geo_path.write_text(json.dumps(_fixture_geojson()), encoding="utf-8")
    _joined_fixture().to_csv(processed / "rendements_climat.csv", index=False)

    table = add_yield_residuals(_joined_fixture())
    fig = plot_synthesis_map(
        _fixture_geojson(),
        wheat_precip_spearman_by_province(table),
        wheat_residual_by_province(table, year=2010),
        year=2010,
    )
    assert len(fig.axes) >= 2
    plt.close(fig)

    png = run_map(processed, tmp_path / "raw", figures)
    assert png.name == README_MAP
    assert png.stat().st_size > 0
    assert (processed / "carte_provinces.csv").exists()
    summary = pd.read_csv(processed / "carte_provinces.csv")
    assert "spearman_r" in summary.columns
