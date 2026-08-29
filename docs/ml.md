# ML basique — régression linéaire (leave-one-year-out)

Complément de l'analyse statistique (`docs/analyse.md`), **pas** un modèle prédictif opérationnel. Cible : **résidu** de rendement (t/ha) en Wallonie, après détrend. Prédicteurs : z-scores de saison (température, pluie, ET0). Validation : chaque année est prédite par un modèle entraîné sur les **autres** années (leave-one-year-out). Baseline naïve : prédire **0** (le rendement reste sur sa tendance).

Cultures évaluées : **8**. Un MAE plus bas que la naïve signifie que le climat aide à situer l'écart à la tendance. Si la meilleure univariée bat les trois variables, la collinéarité (ET0 ≈ température) gonfle l'erreur hors échantillon.

## Erreurs leave-one-year-out (Wallonie)

Unités : t/ha. « Gain vs naïve » = MAE naïve − MAE à trois variables (positif = le climat améliore le diagnostic).

| culture | n | MAE naïve | MAE LOO (3 var.) | R² LOO | MAE meilleure univariée | meilleure univariée | gain vs naïve |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Froment et épeautre | 24 | 0.511 | 0.38 | 0.4 | 0.418 | précipitations saison | 0.131 |
| Betterave sucrière | 25 | 5.002 | 4.919 | -0.049 | 4.858 | précipitations saison | 0.083 |
| Orge | 25 | 0.505 | 0.486 | 0.181 | 0.537 | température saison | 0.019 |
| Colza | 25 | 0.31 | 0.314 | 0.053 | 0.3 | précipitations saison | -0.004 |
| Orge d'hiver | 14 | 0.592 | 0.611 | -0.018 | 0.616 | température saison | -0.019 |
| Maïs grain | 14 | 0.651 | 0.807 | -0.477 | 0.694 | précipitations saison | -0.156 |
| Pomme de terre | 25 | 3.701 | 3.874 | -0.042 | 3.579 | température saison | -0.173 |
| Maïs fourrager | 23 | 2.135 | 2.478 | -0.418 | 2.236 | précipitations saison | -0.343 |

## Zoom : froment et épeautre

Même périmètre que l'analyse statistique : **froment et épeautre**, Wallonie, résidu autour de la tendance linéaire.

- n = 24 années. MAE naïve (prédire 0) = **0.511 t/ha** ; MAE leave-one-out à trois variables = **0.38 t/ha** (R² LOO = 0.4).
- Meilleure univariée : **précipitations saison** (MAE = 0.418 t/ha).
- Le modèle à trois variables fait au moins aussi bien que la meilleure univariée sur ce jeu.
- Coefficients in-sample (lecture, pas la perf) : température -0.456 t/ha par σ, pluie -0.497, ET0 0.309.
- VIF : température 2.97, pluie 1.95, ET0 4.01.
- Plus grand écart LOO : **2016** (résidu -1.791, prédit -0.282).
- Lien avec la Feature 3 : un coefficient de pluie **négatif** va dans le même sens que le Spearman ρ ≈ −0,68 (saison plus humide ↔ résidu plus bas). Ce n'est toujours pas une cause.

Figures : `pictures/experiments/ml-froment-loo.png` et `pictures/readme/ml-mae-vs-naive.png`.

## Garde-fous

- n petit (14–25) : les coefficients et le R² LOO sont bruyants ; la MAE est l'indicateur principal.
- Collinéarité : ET0 de saison et température racontent souvent la même histoire (VIF élevé). D'où la comparaison univariée.
- Pas de pooling des provinces (même décision qu'en Feature 3 : elles ne sont pas des tirages indépendants).
- Coefficients in-sample ≠ performance. La perf se lit uniquement en leave-one-out.
- Corrélation ≠ causalité : pas de prix, maladies, irrigation, variétés au-delà de la droite de tendance.
- Observation 2000–2024 seulement. Un scénario CMIP6 / SSP (Feature 9) n'a de sens qu'**après** ce modèle, en overlay séparé.
