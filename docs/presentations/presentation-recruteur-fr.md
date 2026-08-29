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
![Streamlit](https://img.shields.io/badge/Streamlit-dashboard-FF4B4B?logo=streamlit&logoColor=white)
![matplotlib](https://img.shields.io/badge/matplotlib-figures-11557c)

*Quelles cultures, quelles années — rapport + tableau de bord*

---

## Le problème

Sécheresses, excès de pluie et vagues de chaleur pèsent sur les récoltes
wallonnes. Coopératives, assureurs et administration ont besoin d’une
lecture claire : **quelles cultures, quelles années**.

---

## Les données

Rendements officiels par culture (Wallonie, 2000–2024) croisés avec
température, pluie et évaporation de saison (avril–septembre).

---

## Ce qu’on mesure

On retire d’abord le progrès de long terme des rendements, puis on
regarde si les **écarts** vont de pair avec un climat de saison inhabituel.
Ce n’est **pas** une preuve que le climat a causé la perte.

---

## Constat (Wallonie)

- **Froment** : liaison la plus nette avec la **pluie**. Les saisons
  très humides tendent à être sous la tendance — **2024** surtout.
- **Pomme de terre** : liaison avec la **chaleur** de saison.
- **2018** (chaud et sec) : maïs grain et pomme de terre sous la tendance.

À surveiller : froment les années très humides ; pomme de terre / maïs
grain les étés chauds et secs.

---

## Lecture visuelle

Les barres montrent quelle culture « suit » le plus le climat de saison.
Une étoile : le lien est statistiquement lisible — pas une cause.

![w:880](../../pictures/readme/crop-sensitivity-ranking.png)

---

## Livrables

Rapport statique (README + cartes), contrôle simple « le climat aide-t-il
à situer l’écart ? », et **tableau de bord** pour explorer culture et
période.

Ce n’est pas une prévision, ni un scénario 2050.
