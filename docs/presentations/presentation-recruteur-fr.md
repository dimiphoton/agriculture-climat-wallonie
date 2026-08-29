---
marp: true
theme: default
paginate: true
---

# Rendements agricoles wallons et climat

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-2.x-150458?logo=pandas&logoColor=white)
![scipy](https://img.shields.io/badge/scipy-stats-8CAAE6?logo=scipy&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.x-F7931E?logo=scikitlearn&logoColor=white)

*Quelles cultures, quelles années — et un contrôle simple*

---

## Le problème

Les sécheresses, excès de pluie et vagues de chaleur pèsent sur les récoltes
wallonnes. Coopératives, assureurs et administration ont besoin d’y voir
clair : **quelles cultures, quelles années**.

---

## Les données

Rendements officiels par culture (Wallonie, 2000–2024) croisés avec
température, pluie et évapotranspiration de saison (avril–septembre).

---

## Ce qu’on mesure

On retire d’abord la tendance de long terme des rendements (progrès
agronomique), puis on regarde si les **écarts** vont de pair avec un climat
de saison anormal. Ce n’est **pas** une preuve que le climat a causé la
perte.

---

## Premier constat (Wallonie)

- **Froment** : liaison la plus nette avec la pluie de saison. Les années
  très humides tendent à être sous la tendance — **2024** surtout.
  Les cinq provinces ont le même signe.
- **Pomme de terre** : liaison avec la chaleur de saison.
- **2018** (chaud et sec) : maïs grain et pomme de terre sous la tendance.

---

## Contrôle simple

On vérifie, année par année (sans regarder l’année elle-même), si le
climat de saison aide à situer l’écart de récolte. **Pour le froment,
oui — surtout via la pluie.** Pour la plupart des autres cultures,
ajouter chaleur et évaporation n’améliore pas vraiment le diagnostic.

Ce n’est pas une prévision, ni une cause.

---

## Où on en est

Classement de sensibilité, années à risque, carte provinciale, et ce
contrôle linéaire. Le tableau de bord interactif vient ensuite.
