-- Schéma DuckDB : rendements annuels × climat journalier.
--
-- Le cœur du projet est ici, pas dans un pd.merge. Les deux faits n'ont
-- pas le même grain : rendements = année × culture × territoire ;
-- climat = jour × territoire. La réconciliation (agrégats, saison,
-- z-scores, jointure) est un jeu de VUES, donc lisible et rejouable.
--
-- Pourquoi une vue plutôt qu'une table matérialisée ? Les agrégats
-- (moyenne, cumul, jours au-dessus d'un seuil) sont des *choix* qu'on
-- veut pouvoir relire. Recalculer ~45 000 jours est instantané.

CREATE TABLE dim_annee (
    year INTEGER PRIMARY KEY
);

CREATE TABLE dim_territoire (
    geo VARCHAR PRIMARY KEY,
    geo_label VARCHAR NOT NULL,
    nuts_level VARCHAR NOT NULL  -- 'nuts1' (Wallonie) ou 'nuts2' (province)
);

CREATE TABLE dim_culture (
    crop_code VARCHAR PRIMARY KEY,
    crop_label VARCHAR NOT NULL
);

-- Grain annuel × culture × territoire (Eurostat / Statbel).
CREATE TABLE fact_rendements (
    year INTEGER NOT NULL,
    geo VARCHAR NOT NULL,
    crop_code VARCHAR NOT NULL,
    area_kha DOUBLE,
    production_kt DOUBLE,
    yield_t_ha DOUBLE,
    imputed BOOLEAN NOT NULL,
    PRIMARY KEY (year, geo, crop_code),
    FOREIGN KEY (year) REFERENCES dim_annee (year),
    FOREIGN KEY (geo) REFERENCES dim_territoire (geo),
    FOREIGN KEY (crop_code) REFERENCES dim_culture (crop_code)
);

-- Grain journalier × territoire provincial (ERA5 via Open-Meteo).
-- Pas de ligne BE3 : la Wallonie est une moyenne des cinq points, en vue.
CREATE TABLE fact_climat_quotidien (
    date_jour DATE NOT NULL,
    geo VARCHAR NOT NULL,
    temp_mean_c DOUBLE,
    temp_max_c DOUBLE,
    precip_mm DOUBLE,
    et0_mm DOUBLE,
    PRIMARY KEY (date_jour, geo),
    FOREIGN KEY (geo) REFERENCES dim_territoire (geo)
);

-- ---------------------------------------------------------------------------
-- Réconciliation géographique : Wallonie = moyenne simple des 5 provinces.
-- Ce n'est pas une moyenne pondérée par la SAU (limite documentée).
-- ---------------------------------------------------------------------------
CREATE VIEW v_climat_quotidien AS
SELECT
    c.date_jour,
    c.geo,
    t.geo_label,
    c.temp_mean_c,
    c.temp_max_c,
    c.precip_mm,
    c.et0_mm
FROM fact_climat_quotidien AS c
JOIN dim_territoire AS t ON t.geo = c.geo
UNION ALL
SELECT
    c.date_jour,
    w.geo,
    w.geo_label,
    AVG(c.temp_mean_c),
    AVG(c.temp_max_c),
    AVG(c.precip_mm),
    AVG(c.et0_mm)
FROM fact_climat_quotidien AS c
CROSS JOIN dim_territoire AS w
WHERE w.geo = 'BE3'
GROUP BY c.date_jour, w.geo, w.geo_label;

-- ---------------------------------------------------------------------------
-- Réconciliation temporelle jour → mois.
-- Température : moyenne (un cumul de °C n'a pas de sens).
-- Pluie et ET0 : somme (cumul hydrique / demande évaporative).
-- ---------------------------------------------------------------------------
CREATE VIEW v_climat_mensuel AS
SELECT
    q.geo,
    t.geo_label,
    CAST(year(q.date_jour) AS INTEGER) AS year,
    CAST(month(q.date_jour) AS INTEGER) AS month,
    ROUND(AVG(q.temp_mean_c), 2) AS temp_mean_c,
    ROUND(AVG(q.temp_max_c), 2) AS temp_max_c,
    ROUND(SUM(q.precip_mm), 1) AS precip_mm,
    ROUND(SUM(q.et0_mm), 1) AS et0_mm
FROM v_climat_quotidien AS q
JOIN dim_territoire AS t ON t.geo = q.geo
GROUP BY q.geo, t.geo_label, year(q.date_jour), month(q.date_jour);

-- ---------------------------------------------------------------------------
-- Réconciliation temporelle jour → année, calée sur le grain des rendements.
--
-- Saison de végétation = avril–septembre (compromis unique toutes cultures).
-- Seuils (climatologie belge, pas un optimum cultural) :
--   jour chaud  : Tmax >= 25 °C
--   jour arrosé : précipitation >= 10 mm (pluie notable, pas la bruine)
--   jour sec    : précipitation < 1 mm
-- ---------------------------------------------------------------------------
CREATE VIEW v_climat_annuel AS
SELECT
    geo,
    geo_label,
    year,
    ROUND(AVG(temp_mean_c), 2) AS temp_mean_c,
    ROUND(SUM(precip_mm), 1) AS precip_mm,
    ROUND(SUM(et0_mm), 1) AS et0_mm,
    ROUND(AVG(CASE WHEN month BETWEEN 4 AND 9 THEN temp_mean_c END), 2)
        AS temp_mean_growing_c,
    ROUND(SUM(CASE WHEN month BETWEEN 4 AND 9 THEN precip_mm ELSE 0 END), 1)
        AS precip_growing_mm,
    ROUND(SUM(CASE WHEN month BETWEEN 4 AND 9 THEN et0_mm ELSE 0 END), 1)
        AS et0_growing_mm,
    CAST(SUM(
        CASE WHEN month BETWEEN 4 AND 9 AND temp_max_c >= 25 THEN 1 ELSE 0 END
    ) AS INTEGER) AS n_hot_days_growing,
    CAST(SUM(
        CASE WHEN month BETWEEN 4 AND 9 AND precip_mm >= 10 THEN 1 ELSE 0 END
    ) AS INTEGER) AS n_wet_days_growing,
    CAST(SUM(
        CASE WHEN month BETWEEN 4 AND 9 AND precip_mm < 1 THEN 1 ELSE 0 END
    ) AS INTEGER) AS n_dry_days_growing
FROM (
    SELECT
        q.geo,
        t.geo_label,
        CAST(year(q.date_jour) AS INTEGER) AS year,
        CAST(month(q.date_jour) AS INTEGER) AS month,
        q.temp_mean_c,
        q.temp_max_c,
        q.precip_mm,
        q.et0_mm
    FROM v_climat_quotidien AS q
    JOIN dim_territoire AS t ON t.geo = q.geo
)
GROUP BY geo, geo_label, year;

-- ---------------------------------------------------------------------------
-- Anomalies et z-scores : fenêtre PARTITION BY geo (normale = série 2000–2024
-- de ce territoire, pas une normale OMM 1991–2020). STDDEV_SAMP = ddof=1,
-- comme pandas. Division par zéro → NULL (série constante).
-- ---------------------------------------------------------------------------
CREATE VIEW v_climat_annuel_anomalies AS
SELECT
    year,
    geo,
    geo_label,
    temp_mean_c,
    precip_mm,
    et0_mm,
    temp_mean_growing_c,
    precip_growing_mm,
    et0_growing_mm,
    n_hot_days_growing,
    n_wet_days_growing,
    n_dry_days_growing,
    ROUND(temp_mean_c - AVG(temp_mean_c) OVER (PARTITION BY geo), 2)
        AS temp_mean_c_anom,
    ROUND(
        (temp_mean_c - AVG(temp_mean_c) OVER (PARTITION BY geo))
        / NULLIF(STDDEV_SAMP(temp_mean_c) OVER (PARTITION BY geo), 0),
        3
    ) AS temp_mean_c_z,
    ROUND(precip_mm - AVG(precip_mm) OVER (PARTITION BY geo), 1)
        AS precip_mm_anom,
    ROUND(
        (precip_mm - AVG(precip_mm) OVER (PARTITION BY geo))
        / NULLIF(STDDEV_SAMP(precip_mm) OVER (PARTITION BY geo), 0),
        3
    ) AS precip_mm_z,
    ROUND(et0_mm - AVG(et0_mm) OVER (PARTITION BY geo), 1) AS et0_mm_anom,
    ROUND(
        (et0_mm - AVG(et0_mm) OVER (PARTITION BY geo))
        / NULLIF(STDDEV_SAMP(et0_mm) OVER (PARTITION BY geo), 0),
        3
    ) AS et0_mm_z,
    ROUND(
        temp_mean_growing_c - AVG(temp_mean_growing_c) OVER (PARTITION BY geo),
        2
    ) AS temp_mean_growing_c_anom,
    ROUND(
        (temp_mean_growing_c - AVG(temp_mean_growing_c) OVER (PARTITION BY geo))
        / NULLIF(STDDEV_SAMP(temp_mean_growing_c) OVER (PARTITION BY geo), 0),
        3
    ) AS temp_mean_growing_c_z,
    ROUND(
        precip_growing_mm - AVG(precip_growing_mm) OVER (PARTITION BY geo),
        1
    ) AS precip_growing_mm_anom,
    ROUND(
        (precip_growing_mm - AVG(precip_growing_mm) OVER (PARTITION BY geo))
        / NULLIF(STDDEV_SAMP(precip_growing_mm) OVER (PARTITION BY geo), 0),
        3
    ) AS precip_growing_mm_z,
    ROUND(
        et0_growing_mm - AVG(et0_growing_mm) OVER (PARTITION BY geo),
        1
    ) AS et0_growing_mm_anom,
    ROUND(
        (et0_growing_mm - AVG(et0_growing_mm) OVER (PARTITION BY geo))
        / NULLIF(STDDEV_SAMP(et0_growing_mm) OVER (PARTITION BY geo), 0),
        3
    ) AS et0_growing_mm_z
FROM v_climat_annuel;

-- ---------------------------------------------------------------------------
-- Croisement : INNER JOIN (geo, year). Pas de LEFT : une année orpheline
-- (rendement sans climat ou l'inverse) n'entre pas dans l'analyse.
-- Le climat ne "fan-out" pas : une ligne = culture × territoire × année.
-- ---------------------------------------------------------------------------
CREATE VIEW v_rendements_climat AS
SELECT
    r.year,
    r.geo,
    g.geo_label,
    r.crop_code,
    c.crop_label,
    r.area_kha,
    r.production_kt,
    r.yield_t_ha,
    r.imputed,
    a.temp_mean_c,
    a.precip_mm,
    a.et0_mm,
    a.temp_mean_growing_c,
    a.precip_growing_mm,
    a.et0_growing_mm,
    a.n_hot_days_growing,
    a.n_wet_days_growing,
    a.n_dry_days_growing,
    a.temp_mean_c_anom,
    a.temp_mean_c_z,
    a.precip_mm_anom,
    a.precip_mm_z,
    a.et0_mm_anom,
    a.et0_mm_z,
    a.temp_mean_growing_c_anom,
    a.temp_mean_growing_c_z,
    a.precip_growing_mm_anom,
    a.precip_growing_mm_z,
    a.et0_growing_mm_anom,
    a.et0_growing_mm_z
FROM fact_rendements AS r
INNER JOIN v_climat_annuel_anomalies AS a
    ON a.geo = r.geo AND a.year = r.year
JOIN dim_territoire AS g ON g.geo = r.geo
JOIN dim_culture AS c ON c.crop_code = r.crop_code;

-- ---------------------------------------------------------------------------
-- Tendance pluriannuelle par culture × territoire.
-- regr_slope / regr_intercept = OLS année → t/ha (progrès génétique / technique).
-- Moyenne mobile 5 ans : fenêtre ROWS 4 PRECEDING (pas un pooling provincial).
-- ---------------------------------------------------------------------------
CREATE VIEW v_rendements_residus AS
WITH params AS (
    SELECT
        geo,
        crop_code,
        regr_slope(yield_t_ha, CAST(year AS DOUBLE)) AS slope,
        regr_intercept(yield_t_ha, CAST(year AS DOUBLE)) AS intercept
    FROM fact_rendements
    WHERE yield_t_ha IS NOT NULL
    GROUP BY geo, crop_code
),
resid AS (
    SELECT
        r.year,
        r.geo,
        r.crop_code,
        r.yield_t_ha,
        p.slope AS yield_trend_slope,
        p.intercept + p.slope * r.year AS yield_trend_t_ha,
        r.yield_t_ha - (p.intercept + p.slope * r.year) AS yield_resid_t_ha,
        AVG(r.yield_t_ha) OVER (
            PARTITION BY r.geo, r.crop_code
            ORDER BY r.year
            ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
        ) AS yield_ma5_t_ha
    FROM fact_rendements AS r
    LEFT JOIN params AS p
        ON p.geo = r.geo AND p.crop_code = r.crop_code
)
SELECT
    year,
    geo,
    crop_code,
    yield_t_ha,
    yield_trend_slope,
    ROUND(yield_trend_t_ha, 3) AS yield_trend_t_ha,
    ROUND(yield_resid_t_ha, 3) AS yield_resid_t_ha,
    ROUND(
        yield_resid_t_ha / NULLIF(
            STDDEV_SAMP(yield_resid_t_ha) OVER (PARTITION BY geo, crop_code),
            0
        ),
        3
    ) AS yield_resid_z,
    ROUND(yield_ma5_t_ha, 3) AS yield_ma5_t_ha
FROM resid;

-- ---------------------------------------------------------------------------
-- Indice composite simple de risque climatique par culture × année.
-- Positif seulement si le rendement est sous la tendance ; pondération
-- 40 % pluie / 30 % température / 30 % ET0 (les trois z de saison).
-- Ce n'est pas une probabilité d'assurance, juste un ranking lisible.
-- ---------------------------------------------------------------------------
CREATE VIEW v_indice_risque AS
SELECT
    j.year,
    j.geo,
    j.geo_label,
    j.crop_code,
    j.crop_label,
    r.yield_resid_z,
    j.precip_growing_mm_z,
    j.temp_mean_growing_c_z,
    j.et0_growing_mm_z,
    ROUND(
        GREATEST(0.0, -COALESCE(r.yield_resid_z, 0)) * (
            0.40 * ABS(COALESCE(j.precip_growing_mm_z, 0))
            + 0.30 * ABS(COALESCE(j.temp_mean_growing_c_z, 0))
            + 0.30 * ABS(COALESCE(j.et0_growing_mm_z, 0))
        ),
        3
    ) AS indice_risque
FROM v_rendements_climat AS j
JOIN v_rendements_residus AS r
    ON r.year = j.year AND r.geo = j.geo AND r.crop_code = j.crop_code;

CREATE VIEW v_indice_risque_culture AS
SELECT
    crop_code,
    crop_label,
    ROUND(AVG(indice_risque), 3) AS indice_risque_moyen,
    ROUND(MAX(indice_risque), 3) AS indice_risque_max,
    COUNT(*) FILTER (WHERE indice_risque > 0) AS n_annees_stress
FROM v_indice_risque
WHERE geo = 'BE3'
GROUP BY crop_code, crop_label;
