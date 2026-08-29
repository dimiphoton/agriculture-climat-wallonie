-- Requêtes de croisement et d'analyse.
-- À lancer sur agri_climat.duckdb (après `python -m agri_climat join`).
-- Chaque bloc est autonome : CTE + SELECT. Les vues de sql/schema.sql
-- font déjà le gros de la réconciliation ; ici on pose les questions métier.

-- =============================================================================
-- 1. Grain : du journalier à l'annuel (rappel des agrégats choisis)
-- Pourquoi moyenne / somme / comptage : un cumul de °C n'a pas de sens ;
-- un cumul de mm si ; un seuil (25 °C, 10 mm) capture les extrêmes que
-- la moyenne annuelle lisse.
-- =============================================================================
SELECT
    year,
    geo_label,
    temp_mean_growing_c,
    precip_growing_mm,
    n_hot_days_growing,
    n_wet_days_growing,
    n_dry_days_growing
FROM v_climat_annuel
WHERE geo = 'BE3'
ORDER BY year;

-- =============================================================================
-- 2. Jointure rendements × climat (INNER, clés geo + year)
-- Une ligne = culture × territoire × année. Pas de pooling des provinces.
-- =============================================================================
SELECT
    year,
    geo_label,
    crop_label,
    yield_t_ha,
    precip_growing_mm_z,
    temp_mean_growing_c_z,
    n_hot_days_growing
FROM v_rendements_climat
WHERE geo = 'BE3'
  AND crop_code = 'C1110'  -- froment et épeautre
ORDER BY year;

-- =============================================================================
-- 3. Tendance pluriannuelle (fenêtre + OLS) : progrès vs climat
-- Moyenne mobile 5 ans et résidu après droite année → t/ha.
-- Sans ce detrend, le progrès génétique se confond avec le climat.
-- =============================================================================
SELECT
    r.year,
    c.crop_label,
    r.yield_t_ha,
    r.yield_ma5_t_ha,
    r.yield_trend_t_ha,
    r.yield_resid_t_ha,
    r.yield_resid_z
FROM v_rendements_residus AS r
JOIN dim_culture AS c ON c.crop_code = r.crop_code
WHERE r.geo = 'BE3'
  AND r.crop_code = 'C1110'
ORDER BY r.year;

-- =============================================================================
-- 4. Spearman via les rangs (équivalent de scipy.stats.spearmanr, sans p)
-- corr(rang, rang) = ρ de Spearman. Wallonie seule ; pas de UNION provinciale.
-- =============================================================================
WITH wallonie AS (
    SELECT
        j.crop_code,
        j.crop_label,
        r.yield_resid_t_ha,
        j.precip_growing_mm_z,
        j.temp_mean_growing_c_z,
        j.et0_growing_mm_z
    FROM v_rendements_climat AS j
    JOIN v_rendements_residus AS r
        ON r.year = j.year AND r.geo = j.geo AND r.crop_code = j.crop_code
    WHERE j.geo = 'BE3'
      AND r.yield_resid_t_ha IS NOT NULL
),
ranked AS (
    SELECT
        crop_code,
        crop_label,
        RANK() OVER (PARTITION BY crop_code ORDER BY yield_resid_t_ha) AS rk_resid,
        RANK() OVER (PARTITION BY crop_code ORDER BY precip_growing_mm_z) AS rk_pluie,
        RANK() OVER (PARTITION BY crop_code ORDER BY temp_mean_growing_c_z) AS rk_temp,
        RANK() OVER (PARTITION BY crop_code ORDER BY et0_growing_mm_z) AS rk_et0
    FROM wallonie
)
SELECT
    crop_label,
    ROUND(corr(rk_resid, rk_pluie), 3) AS spearman_pluie,
    ROUND(corr(rk_resid, rk_temp), 3) AS spearman_temp,
    ROUND(corr(rk_resid, rk_et0), 3) AS spearman_et0,
    COUNT(*) AS n
FROM ranked
GROUP BY crop_code, crop_label
ORDER BY ABS(spearman_pluie) DESC;

-- =============================================================================
-- 5. Années atypiques : résidu ≤ −1 σ ET au moins un |z| climatique ≥ 1
-- Filtre joint : on n'étiquette ni un creux technique, ni une année
-- climatique extrême sans signal sur le rendement.
-- =============================================================================
SELECT
    j.year,
    j.crop_label,
    r.yield_resid_z,
    j.precip_growing_mm_z,
    j.temp_mean_growing_c_z,
    j.et0_growing_mm_z
FROM v_rendements_climat AS j
JOIN v_rendements_residus AS r
    ON r.year = j.year AND r.geo = j.geo AND r.crop_code = j.crop_code
WHERE j.geo = 'BE3'
  AND r.yield_resid_z <= -1
  AND (
      ABS(j.precip_growing_mm_z) >= 1
      OR ABS(j.temp_mean_growing_c_z) >= 1
      OR ABS(j.et0_growing_mm_z) >= 1
  )
ORDER BY j.year, j.crop_label;

-- =============================================================================
-- 6. Rang des années à risque (fenêtre RANK) pour le froment wallon
-- =============================================================================
SELECT
    year,
    crop_label,
    indice_risque,
    RANK() OVER (PARTITION BY crop_code ORDER BY indice_risque DESC) AS rang_risque
FROM v_indice_risque
WHERE geo = 'BE3'
  AND crop_code = 'C1110'
ORDER BY rang_risque;

-- =============================================================================
-- 7. Indice composite par culture (vue dédiée, stretch du brief)
-- =============================================================================
SELECT
    crop_label,
    indice_risque_moyen,
    indice_risque_max,
    n_annees_stress
FROM v_indice_risque_culture
ORDER BY indice_risque_moyen DESC;

-- =============================================================================
-- 8. Contrôle de signe provincial (froment × pluie) — pas un pooling
-- Même corrélation de rangs, une fois par province. On vérifie le signe,
-- on ne concatène pas les cinq séries (même année, climat proche).
-- =============================================================================
WITH provincial AS (
    SELECT
        j.geo,
        j.geo_label,
        r.yield_resid_t_ha,
        j.precip_growing_mm_z
    FROM v_rendements_climat AS j
    JOIN v_rendements_residus AS r
        ON r.year = j.year AND r.geo = j.geo AND r.crop_code = j.crop_code
    WHERE j.crop_code = 'C1110'
      AND j.geo != 'BE3'
      AND r.yield_resid_t_ha IS NOT NULL
),
ranked AS (
    SELECT
        geo,
        geo_label,
        RANK() OVER (PARTITION BY geo ORDER BY yield_resid_t_ha) AS rk_resid,
        RANK() OVER (PARTITION BY geo ORDER BY precip_growing_mm_z) AS rk_pluie
    FROM provincial
)
SELECT
    geo_label,
    ROUND(corr(rk_resid, rk_pluie), 3) AS spearman_pluie,
    COUNT(*) AS n
FROM ranked
GROUP BY geo, geo_label
ORDER BY geo;
