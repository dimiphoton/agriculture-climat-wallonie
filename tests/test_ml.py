"""Tests de la baseline linéaire (LOO, naïve, collinéarité)."""

import numpy as np
import pandas as pd

from agri_climat.analyse import add_yield_residuals
from agri_climat.ml import (
    build_ml_markdown,
    evaluate_all_crops,
    evaluate_crop,
    leave_one_out_predictions,
    plot_mae_vs_naive,
    plot_wheat_loo,
    run_ml,
    variance_inflation_factors,
    wheat_loo_detail,
)
from agri_climat.settings import MIN_OBS_ML


def _ml_fixture() -> pd.DataFrame:
    """12 années. Froment lié à la pluie ; ET0 corrélé à la température."""
    years = np.arange(2010, 2022)
    precip_z = np.array(
        [-1.6, -1.1, 0.4, 1.2, 0.1, -0.3, 1.0, 0.5, -1.3, 0.8, -0.4, 0.7]
    )
    temp_z = np.array(
        [0.3, -1.4, 0.1, 1.3, -0.2, 0.6, 1.1, -0.5, -0.8, 0.4, 0.9, -0.7]
    )
    # Collinéarité réaliste, pas parfaite : ET0 ≈ chaleur − un peu de pluie.
    et0_z = 0.7 * temp_z - 0.25 * precip_z
    rows: list[dict[str, object]] = []
    for i, year in enumerate(years):
        yield_wheat = 8.0 + 0.05 * (year - 2010) - 0.5 * precip_z[i]
        rows.append(
            {
                "year": int(year),
                "geo": "BE3",
                "geo_label": "Wallonie",
                "crop_code": "C1110",
                "crop_label": "Froment et épeautre",
                "yield_t_ha": yield_wheat,
                "temp_mean_growing_c_z": temp_z[i],
                "precip_growing_mm_z": precip_z[i],
                "et0_growing_mm_z": et0_z[i],
            }
        )
        yield_beet = 70.0 + 0.3 * (year - 2010) - 0.4 * temp_z[i]
        rows.append(
            {
                "year": int(year),
                "geo": "BE3",
                "geo_label": "Wallonie",
                "crop_code": "R2000",
                "crop_label": "Betterave sucrière",
                "yield_t_ha": yield_beet,
                "temp_mean_growing_c_z": temp_z[i],
                "precip_growing_mm_z": precip_z[i],
                "et0_growing_mm_z": et0_z[i],
            }
        )
    return pd.DataFrame(rows)


def test_loo_retrouve_une_relation_lineaire() -> None:
    """Sur y = 2x, le LOO d'une droite passe (quasi) par les points tenus."""
    x = np.arange(10, dtype=float).reshape(-1, 1)
    y = 2.0 * x.ravel()
    pred = leave_one_out_predictions(x, y)
    assert np.max(np.abs(pred - y)) < 1e-8


def test_vif_infini_si_colonne_dupliquee() -> None:
    """Deux colonnes identiques → VIF infini."""
    col = np.linspace(-1, 1, 12)
    features = np.column_stack([col, col, np.random.default_rng(0).normal(size=12)])
    vifs = variance_inflation_factors(features)
    assert np.isinf(vifs[0])
    assert np.isinf(vifs[1])


def test_froment_pluie_bat_la_naive() -> None:
    """Le froment (construit sur la pluie) a une MAE LOO < MAE naïve."""
    table = add_yield_residuals(_ml_fixture())
    row = evaluate_crop(table, "C1110")
    assert row["n"] >= MIN_OBS_ML
    assert row["mae_loo_multi"] < row["mae_naive"]
    assert row["best_univ_label"] == "précipitations saison"
    assert row["mae_loo_precip_growing_mm_z"] <= row["mae_loo_temp_mean_growing_c_z"]
    # Coefficient de pluie négatif : plus d'eau ↔ résidu plus bas.
    assert row["coef_precip_growing_mm_z"] < 0


def test_n_insuffisant_renvoie_nan() -> None:
    """Moins de MIN_OBS_ML années → métriques à NaN, pas d'exception."""
    short = _ml_fixture().query("crop_code == 'C1110'").head(5)
    row = evaluate_crop(add_yield_residuals(short), "C1110")
    assert np.isnan(row["mae_loo_multi"])
    assert row["n"] == 5


def test_classement_et_rapport() -> None:
    """Le markdown rappelle le LOO, la naïve et le garde-fou causalité."""
    table = add_yield_residuals(_ml_fixture())
    metrics = evaluate_all_crops(table)
    detail = wheat_loo_detail(table)
    assert "C1110" in set(metrics["crop_code"])
    assert not detail.empty
    text = build_ml_markdown(metrics, detail)
    assert "leave-one-year-out" in text
    assert "naïve" in text
    assert "causalité" in text
    assert "Froment" in text


def test_figures_et_run_ml(tmp_path) -> None:
    """PNG et rapport écrits sans fenêtre graphique."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    table = add_yield_residuals(_ml_fixture())
    metrics = evaluate_all_crops(table)
    detail = wheat_loo_detail(table)
    fig_m = plot_mae_vs_naive(metrics)
    assert "naive" in fig_m.axes[0].get_title().lower()
    assert "naive" in fig_m.axes[0].get_ylabel().lower()
    fig_w = plot_wheat_loo(detail)
    assert len(fig_w.axes) == 2
    plt.close(fig_m)
    plt.close(fig_w)

    processed = tmp_path / "processed"
    docs = tmp_path / "docs"
    figures = tmp_path / "figures"
    readme = tmp_path / "readme"
    processed.mkdir()
    _ml_fixture().to_csv(processed / "rendements_climat.csv", index=False)
    report = run_ml(processed, docs, figures, readme)
    assert report.exists()
    assert (processed / "ml_metrics.csv").exists()
    assert (processed / "ml_froment_loo.csv").exists()
    assert (figures / "ml-froment-loo.png").stat().st_size > 0
    assert (readme / "ml-mae-vs-naive.png").stat().st_size > 0
