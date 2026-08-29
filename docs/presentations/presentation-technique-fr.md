---
marp: true
theme: agri
paginate: true
footer: '[Explorer →](../explore-fr.html)'
---

<!-- _class: cover -->
<!-- _paginate: false -->

![bg brightness:0.42](../../pictures/presentations/photos/progress.png)

# Le climat explique-t-il
# les écarts de rendement ?

Wallonie · 2000–2024

---

<!-- _class: split -->

![bg left:46%](../../pictures/presentations/photos/progress.png)

# Ce n'est pas
# le progrès
# génétique.

On retire la tendance. Le climat, c'est l'écart.

---

<!-- _class: chart -->

Froment wallon : observé vs tendance.

![w:920](../../pictures/presentations/detrend-fr.png)

---

<!-- _class: full -->

![bg brightness:0.38](../../pictures/presentations/photos/rain.png)

# Froment × pluie
# ρ ≈ −0,68

Spearman sur le résidu. n petit. Rangs.

---

<!-- _class: chart -->

Les cinq signaux les plus nets.

![w:980](../../pictures/presentations/ranking-fr.png)

---

<!-- _class: split -->

![bg left:40%](../../pictures/presentations/photos/hills.png)

# Pas de pooling.

Même signe partout. Les provinces ne sont pas indépendantes.

![w:480](../../pictures/presentations/map-fr.png)

---

<!-- _class: chart -->

Pourquoi pas un XGBoost ? n = 14–25. Une droite + leave-one-year-out.

![w:640](../../pictures/presentations/mae-fr.png)

---

<!-- _class: dark -->

# Où ça casse.

Un point ERA5 par province.

Un calendrier unique avril–septembre.

Corrélation ≠ cause.

Pas de scénario CMIP6.

---

<!-- _class: cta -->

![bg brightness:0.30](../../pictures/presentations/photos/explore.png)

# Reproduire.

[Explorer en ligne](../explore-fr.html)

`python -m agri_climat run`

`python -m agri_climat dashboard`

Python · scikit-learn · Streamlit
