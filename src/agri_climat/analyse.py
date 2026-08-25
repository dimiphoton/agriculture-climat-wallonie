"""Analyse statistique : sensibilité des rendements au climat observé."""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from scipy.stats import linregress, pearsonr, spearmanr

from agri_climat.data.join import _md_table
from agri_climat.paths import docs_dir, pictures_experiments_dir, processed_dir
from agri_climat.settings import (
    CLIMATE_EXTREME_ABS_Z,
    FOCUS_CROP_CODE,
    GEO_LABELS_FR,
    GROWING_SEASON_Z_COLS,
    MIN_OBS_CORR,
    PROVINCE_CODES,
    WALLONIA_NUTS1,
    YIELD_RESID_Z_MAX,
)

logger = logging.getLogger(__name__)

_CLIMATE_TAGS = (
    ("temp_mean_growing_c_z", "chaud", "froid"),
    ("precip_growing_mm_z", "humide", "sec"),
    ("et0_growing_mm_z", "ET0+", "ET0-"),
)


def add_yield_residuals(joined: pd.DataFrame) -> pd.DataFrame:
    """Ajoute tendance linéaire, résidu et z-score du résidu (culture × geo).

    Le progrès génétique / technique fait souvent monter les rendements dans
    le temps. On retire cette tendance (régression linéaire année → t/ha)
    avant de corréler avec le climat, sinon on mélange les deux effets.

    Parameters
    ----------
    joined
        Table consolidée (une ligne = culture × territoire × année).

    Returns
    -------
    pandas.DataFrame
        Copie avec ``yield_trend_t_ha``, ``yield_resid_t_ha``,
        ``yield_resid_z``, ``yield_trend_slope``.
    """
    out = joined.copy()
    out["yield_trend_t_ha"] = np.nan
    out["yield_resid_t_ha"] = np.nan
    out["yield_resid_z"] = np.nan
    out["yield_trend_slope"] = np.nan

    for _, group in out.groupby(["crop_code", "geo"], sort=False):
        idx = group.index
        years = group["year"].astype(float)
        yields = group["yield_t_ha"].astype(float)
        mask = years.notna() & yields.notna()
        if int(mask.sum()) < 3:
            continue
        fit = linregress(years[mask].to_numpy(), yields[mask].to_numpy())
        trend = fit.intercept + fit.slope * years
        resid = yields - trend
        resid_std = float(resid[mask].std(ddof=1))
        if resid_std == 0 or np.isnan(resid_std):
            resid_z = pd.Series(np.nan, index=idx)
        else:
            resid_z = resid / resid_std
        out.loc[idx, "yield_trend_t_ha"] = trend.round(3)
        out.loc[idx, "yield_resid_t_ha"] = resid.round(3)
        out.loc[idx, "yield_resid_z"] = resid_z.round(3)
        out.loc[idx, "yield_trend_slope"] = round(float(fit.slope), 4)
    return out


def _corr_pair(y: pd.Series, x: pd.Series) -> tuple[int, float, float, float, float]:
    """Spearman et Pearson sur les paires complètes ; NaN si trop peu d'obs."""
    nan = float("nan")
    mask = y.notna() & x.notna()
    n = int(mask.sum())
    if n < MIN_OBS_CORR:
        return n, nan, nan, nan, nan
    ys = y[mask].to_numpy(dtype=float)
    xs = x[mask].to_numpy(dtype=float)
    if np.std(ys, ddof=1) == 0 or np.std(xs, ddof=1) == 0:
        return n, nan, nan, nan, nan
    spearman_r, spearman_p = spearmanr(ys, xs)
    pearson_r, pearson_p = pearsonr(ys, xs)
    return (
        n,
        round(float(spearman_r), 3),
        round(float(spearman_p), 4),
        round(float(pearson_r), 3),
        round(float(pearson_p), 4),
    )


def correlations_by_crop(
    table: pd.DataFrame,
    geo: str = WALLONIA_NUTS1,
) -> pd.DataFrame:
    """Corrélations résidu de rendement × z-scores de saison, par culture.

    Parameters
    ----------
    table
        Table consolidée (résidus ajoutés si absents).
    geo
        Territoire (Wallonie par défaut).

    Returns
    -------
    pandas.DataFrame
        Une ligne par culture × variable climatique.
    """
    work = table[table["geo"] == geo].copy()
    if "yield_resid_t_ha" not in work.columns:
        work = add_yield_residuals(work)
    rows: list[dict[str, object]] = []
    for crop_code, crop_df in work.groupby("crop_code", sort=False):
        label = str(crop_df["crop_label"].iloc[0])
        slope = crop_df["yield_trend_slope"].iloc[0]
        resid = crop_df["yield_resid_t_ha"]
        for col, clim_label in GROWING_SEASON_Z_COLS:
            if col not in crop_df.columns:
                continue
            n_obs, spearman_r, spearman_p, pearson_r, pearson_p = _corr_pair(
                resid, crop_df[col]
            )
            rows.append(
                {
                    "crop_code": crop_code,
                    "crop_label": label,
                    "geo": geo,
                    "climate_var": col,
                    "climate_label": clim_label,
                    "n": n_obs,
                    "trend_t_ha_per_year": slope,
                    "spearman_r": spearman_r,
                    "spearman_p": spearman_p,
                    "pearson_r": pearson_r,
                    "pearson_p": pearson_p,
                }
            )
    return pd.DataFrame(rows)


def sensitivity_ranking(corr: pd.DataFrame) -> pd.DataFrame:
    """Une ligne par culture : variable climatique au |Spearman| le plus fort.

    Parameters
    ----------
    corr
        Sortie de ``correlations_by_crop``.

    Returns
    -------
    pandas.DataFrame
        Cultures triées par |Spearman| décroissant.
    """
    work = corr.dropna(subset=["spearman_r"]).copy()
    if work.empty:
        return work
    work["abs_spearman"] = work["spearman_r"].abs()
    top_idx = work.groupby("crop_code")["abs_spearman"].idxmax()
    ranked = work.loc[top_idx].sort_values("abs_spearman", ascending=False)
    ranked["signif_5pct"] = ranked["spearman_p"] < 0.05
    cols = [
        "crop_label",
        "n",
        "climate_label",
        "spearman_r",
        "spearman_p",
        "pearson_r",
        "pearson_p",
        "signif_5pct",
        "trend_t_ha_per_year",
    ]
    return ranked[cols].reset_index(drop=True)


def _climate_tag_string(row: pd.Series) -> str:
    """Libellés d'aléa (chaud/sec/…) pour les |z| au-delà du seuil."""
    tags: list[str] = []
    for col, pos_label, neg_label in _CLIMATE_TAGS:
        value = row.get(col)
        if value is None or pd.isna(value) or abs(float(value)) < CLIMATE_EXTREME_ABS_Z:
            continue
        tags.append(pos_label if float(value) > 0 else neg_label)
    return ", ".join(tags)


def atypical_years(
    table: pd.DataFrame,
    geo: str = WALLONIA_NUTS1,
) -> pd.DataFrame:
    """Années à bas rendement (hors tendance) et climat de saison extrême.

    Règle : ``yield_resid_z <= -1`` et au moins un |z| climatique de saison
    ``>= 1``. Ce n'est pas un diagnostic causal, juste un filtre joint.

    Parameters
    ----------
    table
        Table consolidée (résidus ajoutés si absents).
    geo
        Territoire (Wallonie par défaut).

    Returns
    -------
    pandas.DataFrame
        Lignes culture × année flaggées, triées par année puis culture.
    """
    work = table[table["geo"] == geo].copy()
    if "yield_resid_z" not in work.columns:
        work = add_yield_residuals(work)
    climate_cols = [col for col, _ in GROWING_SEASON_Z_COLS if col in work.columns]
    extreme = pd.Series(False, index=work.index)
    for col in climate_cols:
        extreme = extreme | (work[col].abs() >= CLIMATE_EXTREME_ABS_Z)
    low_yield = work["yield_resid_z"] <= YIELD_RESID_Z_MAX
    flagged = work.loc[extreme & low_yield].copy()
    if flagged.empty:
        return flagged
    flagged["alea"] = flagged.apply(_climate_tag_string, axis=1)
    cols = [
        "year",
        "crop_label",
        "yield_t_ha",
        "yield_resid_z",
        "temp_mean_growing_c_z",
        "precip_growing_mm_z",
        "et0_growing_mm_z",
        "alea",
    ]
    available = [col for col in cols if col in flagged.columns]
    return (
        flagged[available]
        .sort_values(["year", "crop_label"])
        .reset_index(drop=True)
    )


def provincial_robustness(table: pd.DataFrame) -> pd.DataFrame:
    """Compare le Spearman wallon à la médiane des cinq provinces.

    On ne pool pas les provinces (dépendance spatiale). Même signe = le
    signal Wallonie n'est pas porté par une seule province.

    Parameters
    ----------
    table
        Table consolidée, toutes geos.

    Returns
    -------
    pandas.DataFrame
        Une ligne par culture × variable climatique.
    """
    wallonia = correlations_by_crop(table, geo=WALLONIA_NUTS1)
    if wallonia.empty:
        return wallonia
    province_frames = [
        correlations_by_crop(table, geo=code) for code in PROVINCE_CODES
    ]
    stacked = pd.concat(province_frames, ignore_index=True)
    median_r = (
        stacked.groupby(["crop_code", "climate_var"], as_index=False)["spearman_r"]
        .median()
        .rename(columns={"spearman_r": "spearman_median_provinces"})
    )
    merged = wallonia.merge(median_r, on=["crop_code", "climate_var"], how="left")

    def _n_same_sign(row: pd.Series) -> int:
        r_be3 = row["spearman_r"]
        if pd.isna(r_be3):
            return 0
        subset = stacked[
            (stacked["crop_code"] == row["crop_code"])
            & (stacked["climate_var"] == row["climate_var"])
        ]
        return int((np.sign(subset["spearman_r"]) == np.sign(r_be3)).sum())

    merged["n_provinces_same_sign"] = merged.apply(_n_same_sign, axis=1)
    cols = [
        "crop_label",
        "climate_label",
        "spearman_r",
        "spearman_median_provinces",
        "n_provinces_same_sign",
    ]
    return merged[cols].rename(columns={"spearman_r": "spearman_wallonie"})


def plot_spearman_heatmap(corr: pd.DataFrame) -> Figure:
    """Heatmap Spearman (cultures × variables de saison), Wallonie.

    Parameters
    ----------
    corr
        Sortie de ``correlations_by_crop`` pour un geo.

    Returns
    -------
    matplotlib.figure.Figure
        Figure à enregistrer (pas de ``plt.show``).
    """
    import matplotlib.pyplot as plt

    pivot = corr.pivot(index="crop_label", columns="climate_label", values="spearman_r")
    ordered_cols = [label for _, label in GROWING_SEASON_Z_COLS if label in pivot.columns]
    pivot = pivot.reindex(columns=ordered_cols)
    fig, ax = plt.subplots(figsize=(7.5, 5.0))
    values = pivot.to_numpy(dtype=float)
    image = ax.imshow(values, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(list(pivot.columns), rotation=20, ha="right")
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(list(pivot.index))
    ax.set_title("Spearman : résidu de rendement × climat de saison (Wallonie)")
    for row_i in range(values.shape[0]):
        for col_j in range(values.shape[1]):
            val = values[row_i, col_j]
            if np.isnan(val):
                text = "n/a"
            else:
                text = f"{val:.2f}"
            ax.text(col_j, row_i, text, ha="center", va="center", fontsize=9)
    fig.colorbar(image, ax=ax, fraction=0.046, label="ρ Spearman")
    fig.tight_layout()
    return fig


def plot_wheat_deep_dive(
    table: pd.DataFrame,
    geo: str = WALLONIA_NUTS1,
) -> Figure:
    """Série froment : observé + tendance, résidu z, pluie de saison z.

    Parameters
    ----------
    table
        Table avec résidus.
    geo
        Territoire (Wallonie par défaut).

    Returns
    -------
    matplotlib.figure.Figure
        Trois panneaux, axe des années partagé.
    """
    import matplotlib.pyplot as plt

    work = table[(table["crop_code"] == FOCUS_CROP_CODE) & (table["geo"] == geo)]
    if "yield_resid_z" not in work.columns:
        work = add_yield_residuals(work)
        work = work[(work["crop_code"] == FOCUS_CROP_CODE) & (work["geo"] == geo)]
    wheat = work.sort_values("year")
    geo_label = GEO_LABELS_FR.get(geo, geo)
    fig, axes = plt.subplots(3, 1, figsize=(8.5, 8.0), sharex=True)
    axes[0].plot(wheat["year"], wheat["yield_t_ha"], marker="o", label="observé")
    axes[0].plot(wheat["year"], wheat["yield_trend_t_ha"], color="gray", label="tendance")
    axes[0].set_ylabel("Rendement (t/ha)")
    axes[0].set_title(f"Froment et épeautre — {geo_label}")
    axes[0].legend(loc="best", fontsize=8)

    colors_resid = np.where(wheat["yield_resid_z"] < 0, "indianred", "seagreen")
    axes[1].bar(wheat["year"], wheat["yield_resid_z"], color=colors_resid)
    axes[1].axhline(0, color="black", linewidth=0.8)
    axes[1].axhline(YIELD_RESID_Z_MAX, color="gray", linestyle="--", linewidth=0.8)
    axes[1].set_ylabel("Résidu rendement (z)")

    axes[2].bar(wheat["year"], wheat["precip_growing_mm_z"], color="steelblue")
    axes[2].axhline(0, color="black", linewidth=0.8)
    axes[2].axhline(-CLIMATE_EXTREME_ABS_Z, color="gray", linestyle="--", linewidth=0.8)
    axes[2].axhline(CLIMATE_EXTREME_ABS_Z, color="gray", linestyle="--", linewidth=0.8)
    axes[2].set_ylabel("Pluie saison (z)")
    axes[2].set_xlabel("Année")
    fig.tight_layout()
    return fig


def _fmt_report_tables(ranking: pd.DataFrame, corr: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Renomme les colonnes pour un markdown lisible."""
    ranking_md = ranking.rename(
        columns={
            "crop_label": "culture",
            "climate_label": "variable climatique",
            "spearman_r": "spearman",
            "spearman_p": "p spearman",
            "pearson_r": "pearson",
            "pearson_p": "p pearson",
            "signif_5pct": "p < 0.05",
            "trend_t_ha_per_year": "tendance t/ha/an",
        }
    )
    if "p < 0.05" in ranking_md.columns:
        ranking_md["p < 0.05"] = ranking_md["p < 0.05"].map({True: "oui", False: "non"})
    corr_md = corr.rename(
        columns={
            "crop_label": "culture",
            "climate_label": "variable",
            "spearman_r": "spearman",
            "spearman_p": "p spearman",
            "pearson_r": "pearson",
            "pearson_p": "p pearson",
            "trend_t_ha_per_year": "tendance t/ha/an",
        }
    )
    drop_corr = [col for col in ("crop_code", "geo", "climate_var") if col in corr_md.columns]
    return ranking_md, corr_md.drop(columns=drop_corr)


def _atypical_multi_crop_sentence(atypical: pd.DataFrame) -> str:
    """Phrase sur les années où plusieurs cultures passent le filtre."""
    if atypical.empty or "year" not in atypical.columns:
        return ""
    counts = atypical.groupby("year").size().sort_values(ascending=False)
    multi = counts[counts >= 2]
    if multi.empty:
        return ""
    bits = ", ".join(f"{int(year)} ({int(n)} cultures)" for year, n in multi.items())
    return f"Années avec au moins deux cultures flaggées : {bits}.\n"


def _wheat_narrative(table: pd.DataFrame, corr: pd.DataFrame, atypical: pd.DataFrame) -> list[str]:
    """Quelques phrases générées à partir des chiffres (pas de texte figé)."""
    wheat = table[
        (table["crop_code"] == FOCUS_CROP_CODE) & (table["geo"] == WALLONIA_NUTS1)
    ].dropna(subset=["yield_t_ha"])
    if wheat.empty:
        return ["Pas de données froment pour la Wallonie."]
    slope = float(wheat["yield_trend_slope"].iloc[0])
    wheat_corr = corr[corr["crop_code"] == FOCUS_CROP_CODE].dropna(subset=["spearman_r"])
    lines = [
        "Culture retenue : **froment et épeautre** (série longue, culture "
        "phare wallonne). Le rendement observé est d'abord ramené à un "
        "résidu autour d'une tendance linéaire, pour ne pas attribuer au "
        "climat le progrès agronomique.",
        "",
        f"- Tendance wallonne : **{slope:+.3f} t/ha par an** "
        f"(n = {len(wheat)} années avec rendement).",
    ]
    if not wheat_corr.empty:
        top = wheat_corr.loc[wheat_corr["spearman_r"].abs().idxmax()]
        lines.append(
            f"- Liaison la plus forte (Spearman) : **{top['climate_label']}** "
            f"(ρ = {top['spearman_r']}, p = {top['spearman_p']})."
        )
        precip = wheat_corr[wheat_corr["climate_var"] == "precip_growing_mm_z"]
        if not precip.empty:
            row = precip.iloc[0]
            r_pluie = float(row["spearman_r"])
            # ρ < 0 : plus d'eau en saison ↔ résidu plus bas (pas l'inverse).
            if r_pluie < 0:
                lecture = "saison plus humide ↔ rendement sous la tendance"
            else:
                lecture = "saison plus sèche ↔ rendement sous la tendance"
            lines.append(
                f"- Pluie de saison : ρ = {row['spearman_r']} "
                f"(p = {row['spearman_p']}). Lecture : « {lecture} ». "
                "Ce n'est pas une preuve de cause."
            )
    wheat_atyp = atypical[atypical["crop_label"] == "Froment et épeautre"]
    if wheat_atyp.empty:
        lines.append("- Aucune année froment ne combine résidu ≤ −1 σ et aléa climatique.")
    else:
        years = ", ".join(str(int(y)) for y in wheat_atyp["year"])
        lines.append(
            f"- Années atypiques froment (filtre joint rendement + climat) : **{years}**."
        )
    lines.append("")
    return lines


def build_analyse_markdown(
    ranking: pd.DataFrame,
    corr: pd.DataFrame,
    atypical: pd.DataFrame,
    robust: pd.DataFrame,
    table: pd.DataFrame,
) -> str:
    """Rédige le rapport d'analyse statistique.

    Parameters
    ----------
    ranking, corr, atypical, robust
        Tables produites par les fonctions du module.
    table
        Table avec résidus (pour le zoom froment).

    Returns
    -------
    str
        Texte Markdown (français).
    """
    ranking_md, corr_md = _fmt_report_tables(ranking, corr)
    atypical_md = atypical.rename(
        columns={
            "year": "année",
            "crop_label": "culture",
            "yield_t_ha": "t/ha",
            "yield_resid_z": "résidu z",
            "temp_mean_growing_c_z": "temp z",
            "precip_growing_mm_z": "pluie z",
            "et0_growing_mm_z": "ET0 z",
            "alea": "aléa",
        }
    )
    robust_md = robust.rename(
        columns={
            "crop_label": "culture",
            "climate_label": "variable",
            "spearman_wallonie": "ρ Wallonie",
            "spearman_median_provinces": "ρ médiane provinces",
            "n_provinces_same_sign": "provinces même signe",
        }
    )
    n_crops = ranking["crop_label"].nunique() if not ranking.empty else 0
    parts = [
        "# Analyse statistique — rendements × climat",
        "",
        "Périmètre : **Wallonie (BE3)**, 2000–2024, saison avril–septembre. "
        "Le rendement est d'abord **détrendé** (droite année → t/ha par "
        "culture). On corréle ensuite le **résidu** aux z-scores climatiques "
        "de saison (température, pluie, ET0). Indicateur principal : "
        "**Spearman** (rangs, plus robuste aux extrêmes) ; Pearson en "
        "contrôle. Seuil de lecture : p < 0,05 — ce n'est pas une preuve "
        "de causalité.",
        "",
        f"Cultures classées : **{n_crops}**. Maïs grain et orge d'hiver ont "
        "des séries plus courtes (~14 ans) : la puissance statistique est "
        "plus faible.",
        "",
        "## Classement de sensibilité (Wallonie)",
        "",
        "Pour chaque culture, la variable climatique au |Spearman| le plus "
        "élevé. Un |ρ| fort dit « les années hors tendance de rendement "
        "vont souvent de pair avec cette anomalie climatique » — pas "
        "« cette anomalie a causé la perte ».",
        "",
        _md_table(ranking_md),
        "## Corrélations détaillées",
        "",
        _md_table(corr_md),
        "## Robustesse provinciale",
        "",
        "Médiane du Spearman sur les cinq provinces, **sans pooler** les "
        "lignes (les provinces ne sont pas indépendantes). « Provinces même "
        "signe » : combien de provinces ont le même signe que la Wallonie.",
        "",
        _md_table(robust_md) if not robust.empty else "*(pas de provinces)*\n",
        "## Années atypiques",
        "",
        f"Filtre : résidu de rendement z ≤ {YIELD_RESID_Z_MAX} **et** au "
        f"moins un |z| climatique de saison ≥ {CLIMATE_EXTREME_ABS_Z}. "
        "Une année très sèche sans baisse de rendement (hors tendance) "
        "n'apparaît pas ici, et inversement.",
        "",
        _md_table(atypical_md) if not atypical.empty else "Aucune année ne passe le filtre.\n",
        _atypical_multi_crop_sentence(atypical),
        "## Zoom : froment et épeautre",
        "",
        *_wheat_narrative(table, corr, atypical),
        "Figures : `pictures/experiments/corr-spearman-wallonie.png` et "
        "`pictures/experiments/froment-detrend-climat.png`.",
        "",
        "## Garde-fous (corrélation ≠ causalité)",
        "",
        "- Un point ERA5 par centroïde provincial, Wallonie = moyenne non "
        "pondérée par la SAU : ce n'est pas le climat de la parcelle.",
        "- Calendrier unique avril–septembre pour toutes les cultures "
        "(le maïs et le froment n'ont pas le même calendrier cultural).",
        "- Tendance linéaire : approximation. Un saut méthodologique "
        "Eurostat ou un progrès non linéaire reste dans le résidu.",
        "- Pas de contrôle d'autres facteurs (prix, maladies, irrigation, "
        "changement de variétés au-delà de la droite de tendance).",
        "- Les p-values ne sont pas corrigées pour la multiplicité "
        "(plusieurs cultures × trois variables).",
        "- Observation 2000–2024 seulement : pas de scénario CMIP6 / SSP.",
        "",
    ]
    return "\n".join(parts)


def run_analyse(
    processed_root: Path | None = None,
    docs_root: Path | None = None,
    figures_root: Path | None = None,
) -> Path:
    """Lit la table consolidée, écrit rapport, CSV et PNG (backend Agg).

    Parameters
    ----------
    processed_root
        Dossier ``data/processed``. Défaut : chemins du dépôt.
    docs_root
        Dossier ``docs/`` pour ``analyse.md``.
    figures_root
        Dossier des PNG d'analyse.

    Returns
    -------
    Path
        Chemin de ``docs/analyse.md``.

    Raises
    ------
    FileNotFoundError
        Si ``rendements_climat.csv`` est absent.
    """
    processed = processed_root or processed_dir()
    docs = docs_root or docs_dir()
    figures = figures_root or pictures_experiments_dir()
    csv_path = processed / "rendements_climat.csv"
    if not csv_path.exists():
        raise FileNotFoundError(csv_path)

    joined = pd.read_csv(csv_path)
    table = add_yield_residuals(joined)
    corr = correlations_by_crop(table)
    ranking = sensitivity_ranking(corr)
    atypical = atypical_years(table)
    robust = provincial_robustness(table)

    processed.mkdir(parents=True, exist_ok=True)
    corr_path = processed / "correlations.csv"
    atyp_path = processed / "annees_atypiques.csv"
    corr.to_csv(corr_path, index=False)
    atypical.to_csv(atyp_path, index=False)
    logger.info("Écrit %s", corr_path)
    logger.info("Écrit %s", atyp_path)

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figures.mkdir(parents=True, exist_ok=True)
    heatmap_path = figures / "corr-spearman-wallonie.png"
    wheat_path = figures / "froment-detrend-climat.png"
    fig_h = plot_spearman_heatmap(corr)
    fig_h.savefig(heatmap_path, dpi=120)
    plt.close(fig_h)
    fig_w = plot_wheat_deep_dive(table)
    fig_w.savefig(wheat_path, dpi=120)
    plt.close(fig_w)
    logger.info("Écrit %s", heatmap_path)
    logger.info("Écrit %s", wheat_path)

    docs.mkdir(parents=True, exist_ok=True)
    report_path = docs / "analyse.md"
    report_path.write_text(
        build_analyse_markdown(ranking, corr, atypical, robust, table),
        encoding="utf-8",
    )
    logger.info("Écrit %s", report_path)
    print(ranking.to_string(index=False))
    print(f"\nRapport : {report_path}")
    print(f"Figures : {heatmap_path}")
    print(f"         {wheat_path}")
    return report_path
