"""Tests de l'agrégation climatique quotidienne → mensuel / annuel."""

import pandas as pd

from agri_climat.data.clean_climat import (
    add_wallonia_mean,
    daily_to_monthly,
    monthly_to_annual,
)


def _daily_fixture() -> pd.DataFrame:
    """Deux provinces, janvier (hors saison) et juin (saison de végétation)."""
    rows = []
    for geo, label, t_jan, t_jun, p_jan, p_jun in [
        ("BE32", "Hainaut", 2.0, 18.0, 1.0, 4.0),
        ("BE35", "Namur", 4.0, 20.0, 3.0, 6.0),
    ]:
        rows.append(
            {
                "date": pd.Timestamp("2020-01-15"),
                "geo": geo,
                "geo_label": label,
                "temp_mean_c": t_jan,
                "temp_max_c": t_jan + 3,
                "precip_mm": p_jan,
                "et0_mm": 0.5,
            }
        )
        rows.append(
            {
                "date": pd.Timestamp("2020-06-15"),
                "geo": geo,
                "geo_label": label,
                "temp_mean_c": t_jun,
                "temp_max_c": t_jun + 5,
                "precip_mm": p_jun,
                "et0_mm": 3.0,
            }
        )
    return pd.DataFrame(rows)


def test_mensuel_somme_precip_moyenne_temp() -> None:
    """La pluie est sommée, la température moyennée."""
    monthly = daily_to_monthly(_daily_fixture())
    hainaut_juin = monthly[
        (monthly["geo"] == "BE32") & (monthly["month"] == 6)
    ].iloc[0]
    assert hainaut_juin["precip_mm"] == 4.0
    assert hainaut_juin["temp_mean_c"] == 18.0


def test_annuel_saison_vegetation_et_moyenne_wallonie() -> None:
    """Avril–septembre isolé ; la Wallonie est la moyenne des provinces."""
    monthly = daily_to_monthly(_daily_fixture())
    annual = add_wallonia_mean(monthly_to_annual(monthly))
    hainaut = annual[annual["geo"] == "BE32"].iloc[0]
    assert hainaut["precip_mm"] == 5.0  # 1 + 4
    assert hainaut["precip_growing_mm"] == 4.0  # juin seulement
    wallonie = annual[annual["geo"] == "BE3"].iloc[0]
    assert wallonie["precip_mm"] == 7.0  # moyenne de 5 et 9
    assert wallonie["geo_label"] == "Wallonie"
