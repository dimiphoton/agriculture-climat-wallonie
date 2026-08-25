"""Tests du nettoyage des rendements Eurostat."""

from agri_climat.data.clean_rendements import clean_rendements, parse_eurostat_obs

# TSV minimal : production wallonne 2011 volontairement aberrante (1,17 kt).
_FIXTURE = """freq,crops,strucpro,geo\\TIME_PERIOD	2010 	2011 	2012
A,C1110,AR_THS_HA,BE3	140.00 	140.00 	140.00
A,C1110,AR_THS_HA,BE31	20.00 	20.00 	20.00
A,C1110,AR_THS_HA,BE32	50.00 	50.00 	50.00
A,C1110,AR_THS_HA,BE33	25.00 	25.00 	25.00
A,C1110,AR_THS_HA,BE34	10.00 	10.00 	10.00
A,C1110,AR_THS_HA,BE35	35.00 	35.00 	35.00
A,C1110,HPRD_HUMD_EU_THS_T,BE3	1120.00 	1.17 	1180.00
A,C1110,HPRD_HUMD_EU_THS_T,BE31	160.00 	160.00 	170.00
A,C1110,HPRD_HUMD_EU_THS_T,BE32	400.00 	400.00 	420.00
A,C1110,HPRD_HUMD_EU_THS_T,BE33	200.00 	200.00 	210.00
A,C1110,HPRD_HUMD_EU_THS_T,BE34	80.00 	80.00 	85.00
A,C1110,HPRD_HUMD_EU_THS_T,BE35	280.00 	280.00 	295.00
"""


def test_parse_obs_manquant_et_flag() -> None:
    """Les cellules vides, ':' et flags Eurostat sont gérés."""
    assert pd_isna(parse_eurostat_obs(":"))
    assert pd_isna(parse_eurostat_obs(""))
    assert parse_eurostat_obs("196.42 e") == 196.42
    assert parse_eurostat_obs("8.09") == 8.09


def pd_isna(value: float) -> bool:
    """Évite d'importer pandas juste pour isna dans l'assert de parse."""
    return value != value


def test_rendement_calcule_et_imputation_be3() -> None:
    """Le rendement est production/superficie ; BE3 2011 est imputé."""
    table = clean_rendements(_FIXTURE)
    hainaut_2012 = table[
        (table["geo"] == "BE32") & (table["year"] == 2012)
    ].iloc[0]
    assert hainaut_2012["yield_t_ha"] == 8.4  # 420 / 50

    wallonie_2010 = table[
        (table["geo"] == "BE3") & (table["year"] == 2010)
    ].iloc[0]
    assert not bool(wallonie_2010["imputed"])
    assert wallonie_2010["yield_t_ha"] == 8.0  # 1120 / 140

    wallonie_2011 = table[
        (table["geo"] == "BE3") & (table["year"] == 2011)
    ].iloc[0]
    assert bool(wallonie_2011["imputed"])
    # Somme provinces : 160+400+200+80+280 = 1120 kt / 140 kha = 8 t/ha
    assert wallonie_2011["production_kt"] == 1120.0
    assert wallonie_2011["yield_t_ha"] == 8.0
