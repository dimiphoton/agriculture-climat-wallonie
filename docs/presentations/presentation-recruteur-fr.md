---
marp: true
theme: default
paginate: true
---

# Rendements agricoles wallons et climat

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-2.x-150458?logo=pandas&logoColor=white)
![scipy](https://img.shields.io/badge/scipy-stats-8CAAE6?logo=scipy&logoColor=white)

*Feature 3 : quelles cultures, quelles années*

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

- **Froment** : liaison la plus nette avec la pluie de saison (ρ ≈ −0,68).
  Les années très humides tendent à être sous la tendance — **2024** surtout.
  Les cinq provinces ont le même signe.
- **Pomme de terre** : liaison avec la chaleur de saison (ρ ≈ −0,46).
- **2018** (chaud et sec) : maïs grain et pomme de terre sous la tendance.

Ce sont des **corrélations**, pas des causes : un point météo par province,
pas le climat de la parcelle.

---

## Où on en est

Un classement de sensibilité par culture, une liste d’années atypiques, et
un zoom sur le froment. Les graphiques « vitrine » et le tableau de bord
viennent ensuite.
