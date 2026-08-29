"""Baseline linéaire : résidu de rendement ~ z-scores climatiques (LOO)."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score

from agri_climat.analyse import add_yield_residuals
from agri_climat.data.join import _md_table
from agri_climat.paths import docs_dir, pictures_experiments_dir, pictures_readme_dir, processed_dir
from agri_climat.settings import (
    CROP_LABELS_EN,
    CROP_LABELS_FR,
    FOCUS_CROP_CODE,
    GROWING_SEASON_Z_COLS,
    MIN_OBS_ML,
    WALLONIA_NUTS1,
)

if TYPE_CHECKING:
    from matplotlib.figure import Figure

logger = logging.getLogger(__name__)

README_ML_FIGURE = "ml-mae-vs-naive.png"
EXPERIMENT_WHEAT_FIGURE = "ml-froment-loo.png"

_FEATURE_COLS: tuple[str, ...] = tuple(col for col, _ in GROWING_SEASON_Z_COLS)
_FR_LABEL_TO_CODE: dict[str, str] = {label: code for code, label in CROP_LABELS_FR.items()}


def leave_one_out_predictions(features: np.ndarray, target: np.ndarray) -> np.ndarray:
    """Prédiction de chaque année par un modèle entraîné sur les autres.

    Leave-one-out explicite : avec n ≈ 14–25, un split aléatoire 80/20
    ne laisserait que 3–5 points de test, trop bruité.

    Parameters
    ----------
    features
        Matrice (n, p) des prédicteurs.
    target
        Vecteur (n,) de la cible.

    Returns
    -------
    numpy.ndarray
        Prédictions de même longueur que ``target``.
    """
    n_rows = len(target)
    preds = np.empty(n_rows, dtype=float)
    for i in range(n_rows):
        train = np.ones(n_rows, dtype=bool)
        train[i] = False
        model = LinearRegression().fit(features[train], target[train])
        preds[i] = float(model.predict(features[i : i + 1])[0])
    return preds


def variance_inflation_factors(features: np.ndarray) -> np.ndarray:
    """VIF de chaque colonne : 1 / (1 − R² de la régression sur les autres).

    Un VIF élevé (souvent > 5) signale que le prédicteur est quasi une
    combinaison linéaire des autres — ici ET0 et température de saison.

    Parameters
    ----------
    features
        Matrice (n, p).

    Returns
    -------
    numpy.ndarray
        Un VIF par colonne ; ``inf`` si R² = 1.
    """
    n_features = features.shape[1]
    vifs = np.ones(n_features, dtype=float)
    for j in range(n_features):
        others = np.delete(features, j, axis=1)
        y_j = features[:, j]
        if np.std(y_j, ddof=1) == 0 or others.shape[1] == 0:
            vifs[j] = np.nan
            continue
        pred = LinearRegression().fit(others, y_j).predict(others)
        ss_res = float(np.sum((y_j - pred) ** 2))
        ss_tot = float(np.sum((y_j - y_j.mean()) ** 2))
        if ss_tot == 0:
            vifs[j] = np.nan
            continue
        r_squared = 1.0 - ss_res / ss_tot
        if r_squared >= 1.0 - 1e-12:
            vifs[j] = np.inf
        else:
            vifs[j] = 1.0 / (1.0 - r_squared)
    return vifs


def _crop_panel(table: pd.DataFrame, crop_code: str, geo: str) -> pd.DataFrame:
    """Lignes d'une culture × territoire, résidus et climat complets."""
    work = table[(table["crop_code"] == crop_code) & (table["geo"] == geo)].copy()
    if "yield_resid_t_ha" not in work.columns:
        work = add_yield_residuals(work)
        work = work[(work["crop_code"] == crop_code) & (work["geo"] == geo)]
    needed = ["year", "yield_resid_t_ha", *_FEATURE_COLS]
    available = [col for col in needed if col in work.columns]
    return work.dropna(subset=available).sort_values("year")


def _empty_metrics_row(crop_code: str, crop_label: str, n_obs: int) -> dict[str, object]:
    """Ligne de métriques vide (n insuffisant)."""
    row: dict[str, object] = {
        "crop_code": crop_code,
        "crop_label": crop_label,
        "n": n_obs,
        "mae_naive": float("nan"),
        "mae_loo_multi": float("nan"),
        "r2_loo_multi": float("nan"),
        "mae_loo_best_univ": float("nan"),
        "best_univ_label": "",
        "mae_beats_naive": False,
    }
    for col, label in GROWING_SEASON_Z_COLS:
        row[f"mae_loo_{col}"] = float("nan")
        row[f"coef_{col}"] = float("nan")
        row[f"vif_{col}"] = float("nan")
    row["intercept"] = float("nan")
    return row


def evaluate_crop(
    table: pd.DataFrame,
    crop_code: str,
    geo: str = WALLONIA_NUTS1,
) -> dict[str, object]:
    """MAE naïve vs LOO (multi et univarié) + coefficients in-sample.

    La performance se lit sur le leave-one-out. Les coefficients OLS sur
    tout l'échantillon servent uniquement à la lecture (t/ha par σ).

    Parameters
    ----------
    table
        Table consolidée (résidus ajoutés si absents).
    crop_code
        Code Eurostat (ex. ``C1110``).
    geo
        Territoire (Wallonie par défaut).

    Returns
    -------
    dict
        Métriques et coefficients pour une culture.
    """
    panel = _crop_panel(table, crop_code, geo)
    label = (
        str(panel["crop_label"].iloc[0])
        if not panel.empty and "crop_label" in panel.columns
        else CROP_LABELS_FR.get(crop_code, crop_code)
    )
    n_obs = len(panel)
    if n_obs < MIN_OBS_ML:
        return _empty_metrics_row(crop_code, label, n_obs)

    target = panel["yield_resid_t_ha"].to_numpy(dtype=float)
    features = panel[list(_FEATURE_COLS)].to_numpy(dtype=float)
    # Baseline : prédire 0, i.e. « le rendement reste sur sa tendance ».
    mae_naive = float(np.mean(np.abs(target)))
    pred_multi = leave_one_out_predictions(features, target)
    mae_multi = float(mean_absolute_error(target, pred_multi))
    r2_multi = float(r2_score(target, pred_multi))

    univ_mae: dict[str, float] = {}
    for col, clim_label in GROWING_SEASON_Z_COLS:
        pred_u = leave_one_out_predictions(panel[[col]].to_numpy(dtype=float), target)
        univ_mae[clim_label] = float(mean_absolute_error(target, pred_u))
    best_label = min(univ_mae, key=univ_mae.get)

    fitted = LinearRegression().fit(features, target)
    vifs = variance_inflation_factors(features)

    row: dict[str, object] = {
        "crop_code": crop_code,
        "crop_label": label,
        "n": n_obs,
        "mae_naive": round(mae_naive, 3),
        "mae_loo_multi": round(mae_multi, 3),
        "r2_loo_multi": round(r2_multi, 3),
        "mae_loo_best_univ": round(univ_mae[best_label], 3),
        "best_univ_label": best_label,
        "mae_beats_naive": mae_multi < mae_naive,
        "intercept": round(float(fitted.intercept_), 3),
    }
    for i, (col, clim_label) in enumerate(GROWING_SEASON_Z_COLS):
        row[f"mae_loo_{col}"] = round(univ_mae[clim_label], 3)
        row[f"coef_{col}"] = round(float(fitted.coef_[i]), 3)
        vif_val = float(vifs[i])
        row[f"vif_{col}"] = vif_val if np.isinf(vif_val) else round(vif_val, 2)
    return row


def evaluate_all_crops(
    table: pd.DataFrame,
    geo: str = WALLONIA_NUTS1,
) -> pd.DataFrame:
    """Une ligne de métriques ML par culture (Wallonie par défaut).

    Parameters
    ----------
    table
        Table consolidée, toutes cultures.
    geo
        Territoire.

    Returns
    -------
    pandas.DataFrame
        Cultures triées par gain de MAE (naïve − multi) décroissant.
    """
    work = table.copy()
    if "yield_resid_t_ha" not in work.columns:
        work = add_yield_residuals(work)
    codes = list(dict.fromkeys(work.loc[work["geo"] == geo, "crop_code"].tolist()))
    rows = [evaluate_crop(work, str(code), geo=geo) for code in codes]
    metrics = pd.DataFrame(rows)
    if metrics.empty:
        return metrics
    metrics["mae_gain"] = (metrics["mae_naive"] - metrics["mae_loo_multi"]).round(3)
    return metrics.sort_values("mae_gain", ascending=False, na_position="last").reset_index(
        drop=True
    )


def wheat_loo_detail(
    table: pd.DataFrame,
    geo: str = WALLONIA_NUTS1,
) -> pd.DataFrame:
    """Série froment : résidu observé, prédiction LOO et erreur.

    Parameters
    ----------
    table
        Table consolidée.
    geo
        Territoire (Wallonie par défaut).

    Returns
    -------
    pandas.DataFrame
        Une ligne par année.
    """
    panel = _crop_panel(table, FOCUS_CROP_CODE, geo)
    if len(panel) < MIN_OBS_ML:
        return pd.DataFrame()
    target = panel["yield_resid_t_ha"].to_numpy(dtype=float)
    features = panel[list(_FEATURE_COLS)].to_numpy(dtype=float)
    pred = leave_one_out_predictions(features, target)
    out = panel[["year", "yield_resid_t_ha"]].copy()
    out["pred_loo"] = np.round(pred, 3)
    out["error_loo"] = np.round(target - pred, 3)
    return out.reset_index(drop=True)


def _crop_label_en(fr_label: str) -> str:
    """Traduit un libellé culture FR vers l'anglais du README."""
    code = _FR_LABEL_TO_CODE.get(fr_label)
    if code is None:
        return fr_label
    return CROP_LABELS_EN.get(code, fr_label)


def _fmt_vif(value: object) -> str:
    """Affiche un VIF (infini si collinéarité parfaite)."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "n/a"
    if isinstance(value, (float, int, np.floating)) and np.isinf(float(value)):
        return "∞"
    return str(value)


def plot_mae_vs_naive(metrics: pd.DataFrame) -> Figure:
    """Ratio MAE / naïve : < 1 = le climat bat le « reste sur la tendance ».

    Les rendements n'ont pas la même échelle (betterave vs colza) : le ratio
    rend les cultures comparables. La ligne à 1 est la baseline naïve.

    Parameters
    ----------
    metrics
        Sortie de ``evaluate_all_crops``.

    Returns
    -------
    matplotlib.figure.Figure
        Figure README (libellés anglais).
    """
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9.0, 4.8))
    work = metrics.dropna(subset=["mae_naive", "mae_loo_multi"]).copy()
    if work.empty:
        ax.set_title("No ML metrics available")
        fig.tight_layout()
        return fig

    work = work.sort_values("mae_gain", ascending=False)
    naive = work["mae_naive"].to_numpy(dtype=float)
    ratio_multi = work["mae_loo_multi"].to_numpy(dtype=float) / naive
    ratio_univ = work["mae_loo_best_univ"].to_numpy(dtype=float) / naive
    x_pos = np.arange(len(work))
    width = 0.35
    ax.bar(
        x_pos - width / 2,
        ratio_multi,
        width,
        label="Linear (3 climate z-scores)",
        color="#4c72b0",
    )
    ax.bar(
        x_pos + width / 2,
        ratio_univ,
        width,
        label="Best single climate variable",
        color="#dd8452",
    )
    ax.axhline(1.0, color="black", linewidth=0.9, linestyle="--", label="Naive (ratio = 1)")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(
        [_crop_label_en(str(label)) for label in work["crop_label"]],
        rotation=25,
        ha="right",
    )
    ax.set_ylabel("LOO MAE / naive MAE")
    ax.set_title("Does climate beat a naive guess of the yield residual?")
    ax.legend(loc="upper right", fontsize=8, frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return fig


def plot_wheat_loo(detail: pd.DataFrame) -> Figure:
    """Série et nuage : résidu froment observé vs prédiction leave-one-out.

    Parameters
    ----------
    detail
        Sortie de ``wheat_loo_detail``.

    Returns
    -------
    matplotlib.figure.Figure
        Deux panneaux (français, dossier experiments).
    """
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 1, figsize=(8.5, 6.8))
    if detail.empty:
        axes[0].set_title("Pas de série froment")
        fig.tight_layout()
        return fig

    axes[0].plot(
        detail["year"],
        detail["yield_resid_t_ha"],
        marker="o",
        label="résidu observé",
    )
    axes[0].plot(
        detail["year"],
        detail["pred_loo"],
        marker="s",
        linestyle="--",
        label="prédiction LOO",
    )
    axes[0].axhline(0, color="black", linewidth=0.8)
    axes[0].set_ylabel("Résidu (t/ha)")
    axes[0].set_title("Froment — résidu observé vs prédiction leave-one-year-out")
    axes[0].legend(loc="best", fontsize=8)

    axes[1].scatter(detail["yield_resid_t_ha"], detail["pred_loo"], color="#4c72b0")
    vals = np.concatenate(
        [
            detail["yield_resid_t_ha"].to_numpy(dtype=float),
            detail["pred_loo"].to_numpy(dtype=float),
        ]
    )
    lo, hi = float(np.nanmin(vals)), float(np.nanmax(vals))
    pad = 0.05 * (hi - lo if hi > lo else 1.0)
    axes[1].plot([lo - pad, hi + pad], [lo - pad, hi + pad], color="gray", linewidth=0.8)
    axes[1].set_xlabel("Résidu observé (t/ha)")
    axes[1].set_ylabel("Prédiction LOO (t/ha)")
    fig.tight_layout()
    return fig


def _metrics_for_markdown(metrics: pd.DataFrame) -> pd.DataFrame:
    """Colonnes lisibles pour le rapport."""
    cols = [
        "crop_label",
        "n",
        "mae_naive",
        "mae_loo_multi",
        "r2_loo_multi",
        "mae_loo_best_univ",
        "best_univ_label",
        "mae_gain",
    ]
    renamed = metrics[cols].rename(
        columns={
            "crop_label": "culture",
            "mae_naive": "MAE naïve",
            "mae_loo_multi": "MAE LOO (3 var.)",
            "r2_loo_multi": "R² LOO",
            "mae_loo_best_univ": "MAE meilleure univariée",
            "best_univ_label": "meilleure univariée",
            "mae_gain": "gain vs naïve",
        }
    )
    return renamed


def _wheat_ml_narrative(metrics: pd.DataFrame, detail: pd.DataFrame) -> list[str]:
    """Phrases générées à partir des chiffres froment."""
    wheat = metrics[metrics["crop_code"] == FOCUS_CROP_CODE]
    if wheat.empty:
        return ["Pas de métriques froment."]
    row = wheat.iloc[0]
    coef_p = row.get("coef_precip_growing_mm_z")
    coef_t = row.get("coef_temp_mean_growing_c_z")
    coef_e = row.get("coef_et0_growing_mm_z")
    lines = [
        "Même périmètre que l'analyse statistique : **froment et épeautre**, "
        "Wallonie, résidu autour de la tendance linéaire.",
        "",
        f"- n = {int(row['n'])} années. MAE naïve (prédire 0) = "
        f"**{row['mae_naive']} t/ha** ; MAE leave-one-out à trois variables = "
        f"**{row['mae_loo_multi']} t/ha** (R² LOO = {row['r2_loo_multi']}).",
        f"- Meilleure univariée : **{row['best_univ_label']}** "
        f"(MAE = {row['mae_loo_best_univ']} t/ha).",
    ]
    multi = float(row["mae_loo_multi"]) if pd.notna(row["mae_loo_multi"]) else np.nan
    univ = float(row["mae_loo_best_univ"]) if pd.notna(row["mae_loo_best_univ"]) else np.nan
    if pd.notna(multi) and pd.notna(univ):
        if univ < multi:
            lines.append(
                "- La meilleure univariée **bat** le modèle à trois variables : "
                "ajouter température et ET0 n'améliore pas le hors-échantillon "
                "(collinéarité probable)."
            )
        else:
            lines.append(
                "- Le modèle à trois variables fait au moins aussi bien que la "
                "meilleure univariée sur ce jeu."
            )
    lines.append(
        f"- Coefficients in-sample (lecture, pas la perf) : "
        f"température {coef_t} t/ha par σ, pluie {coef_p}, ET0 {coef_e}."
    )
    lines.append(
        f"- VIF : température {_fmt_vif(row.get('vif_temp_mean_growing_c_z'))}, "
        f"pluie {_fmt_vif(row.get('vif_precip_growing_mm_z'))}, "
        f"ET0 {_fmt_vif(row.get('vif_et0_growing_mm_z'))}."
    )
    if not detail.empty:
        worst = detail.loc[detail["error_loo"].abs().idxmax()]
        lines.append(
            f"- Plus grand écart LOO : **{int(worst['year'])}** "
            f"(résidu {worst['yield_resid_t_ha']}, prédit {worst['pred_loo']})."
        )
    lines.append(
        "- Lien avec la Feature 3 : un coefficient de pluie **négatif** "
        "va dans le même sens que le Spearman ρ ≈ −0,68 (saison plus "
        "humide ↔ résidu plus bas). Ce n'est toujours pas une cause."
    )
    lines.append("")
    return lines


def build_ml_markdown(metrics: pd.DataFrame, detail: pd.DataFrame) -> str:
    """Rédige le rapport ML.

    Parameters
    ----------
    metrics
        Sortie de ``evaluate_all_crops``.
    detail
        Sortie de ``wheat_loo_detail``.

    Returns
    -------
    str
        Texte Markdown (français).
    """
    table_md = _metrics_for_markdown(metrics) if not metrics.empty else pd.DataFrame()
    n_ok = int(metrics["mae_loo_multi"].notna().sum()) if not metrics.empty else 0
    parts = [
        "# ML basique — régression linéaire (leave-one-year-out)",
        "",
        "Complément de l'analyse statistique (`docs/analyse.md`), **pas** un "
        "modèle prédictif opérationnel. Cible : **résidu** de rendement "
        "(t/ha) en Wallonie, après détrend. Prédicteurs : z-scores de saison "
        "(température, pluie, ET0). Validation : chaque année est prédite par "
        "un modèle entraîné sur les **autres** années (leave-one-year-out). "
        "Baseline naïve : prédire **0** (le rendement reste sur sa tendance).",
        "",
        f"Cultures évaluées : **{n_ok}**. Un MAE plus bas que la naïve "
        "signifie que le climat aide à situer l'écart à la tendance. Si la "
        "meilleure univariée bat les trois variables, la collinéarité "
        "(ET0 ≈ température) gonfle l'erreur hors échantillon.",
        "",
        "## Erreurs leave-one-year-out (Wallonie)",
        "",
        "Unités : t/ha. « Gain vs naïve » = MAE naïve − MAE à trois variables "
        "(positif = le climat améliore le diagnostic).",
        "",
        _md_table(table_md) if not table_md.empty else "*(pas de métriques)*\n",
        "## Zoom : froment et épeautre",
        "",
        *_wheat_ml_narrative(metrics, detail),
        f"Figures : `pictures/experiments/{EXPERIMENT_WHEAT_FIGURE}` et "
        f"`pictures/readme/{README_ML_FIGURE}`.",
        "",
        "## Garde-fous",
        "",
        "- n petit (14–25) : les coefficients et le R² LOO sont bruyants ; "
        "la MAE est l'indicateur principal.",
        "- Collinéarité : ET0 de saison et température racontent souvent la "
        "même histoire (VIF élevé). D'où la comparaison univariée.",
        "- Pas de pooling des provinces (même décision qu'en Feature 3 : "
        "elles ne sont pas des tirages indépendants).",
        "- Coefficients in-sample ≠ performance. La perf se lit uniquement "
        "en leave-one-out.",
        "- Corrélation ≠ causalité : pas de prix, maladies, irrigation, "
        "variétés au-delà de la droite de tendance.",
        "- Observation 2000–2024 seulement. Un scénario CMIP6 / SSP "
        "(Feature 9) n'a de sens qu'**après** ce modèle, en overlay séparé.",
        "",
    ]
    return "\n".join(parts)


def run_ml(
    processed_root: Path | None = None,
    docs_root: Path | None = None,
    figures_root: Path | None = None,
    readme_root: Path | None = None,
) -> Path:
    """Lit la table consolidée, écrit rapport, CSV et PNG (backend Agg).

    Parameters
    ----------
    processed_root
        Dossier ``data/processed``. Défaut : chemins du dépôt.
    docs_root
        Dossier ``docs/`` pour ``ml.md``.
    figures_root
        Dossier des PNG d'analyse (français).
    readme_root
        Dossier des PNG README (anglais).

    Returns
    -------
    Path
        Chemin de ``docs/ml.md``.

    Raises
    ------
    FileNotFoundError
        Si ``rendements_climat.csv`` est absent.
    """
    processed = processed_root or processed_dir()
    docs = docs_root or docs_dir()
    figures = figures_root or pictures_experiments_dir()
    readme = readme_root or pictures_readme_dir()
    csv_path = processed / "rendements_climat.csv"
    if not csv_path.exists():
        raise FileNotFoundError(csv_path)

    joined = pd.read_csv(csv_path)
    table = add_yield_residuals(joined)
    metrics = evaluate_all_crops(table)
    detail = wheat_loo_detail(table)

    processed.mkdir(parents=True, exist_ok=True)
    metrics_path = processed / "ml_metrics.csv"
    detail_path = processed / "ml_froment_loo.csv"
    metrics.to_csv(metrics_path, index=False)
    detail.to_csv(detail_path, index=False)
    logger.info("Écrit %s", metrics_path)
    logger.info("Écrit %s", detail_path)

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figures.mkdir(parents=True, exist_ok=True)
    readme.mkdir(parents=True, exist_ok=True)
    wheat_fig_path = figures / EXPERIMENT_WHEAT_FIGURE
    readme_fig_path = readme / README_ML_FIGURE
    fig_w = plot_wheat_loo(detail)
    fig_w.savefig(wheat_fig_path, dpi=120)
    plt.close(fig_w)
    fig_m = plot_mae_vs_naive(metrics)
    fig_m.savefig(readme_fig_path, dpi=140, bbox_inches="tight")
    plt.close(fig_m)
    logger.info("Écrit %s", wheat_fig_path)
    logger.info("Écrit %s", readme_fig_path)

    docs.mkdir(parents=True, exist_ok=True)
    report_path = docs / "ml.md"
    report_path.write_text(build_ml_markdown(metrics, detail), encoding="utf-8")
    logger.info("Écrit %s", report_path)
    printable = metrics[
        ["crop_label", "n", "mae_naive", "mae_loo_multi", "r2_loo_multi", "best_univ_label"]
    ]
    print(printable.to_string(index=False))
    print(f"\nRapport : {report_path}")
    print(f"Figures : {wheat_fig_path}")
    print(f"         {readme_fig_path}")
    return report_path
