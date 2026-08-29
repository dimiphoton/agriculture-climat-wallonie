---
marp: true
theme: agri
paginate: true
footer: '[Explore →](../explore-en.html)'
---

<!-- _class: cover -->
<!-- _paginate: false -->

![bg brightness:0.42](../../pictures/presentations/photos/progress.png)

# Does climate explain
# yield gaps?

Wallonia · 2000–2024

---

<!-- _class: split -->

![bg left:46%](../../pictures/presentations/photos/progress.png)

# This is not
# genetic progress.

We remove the trend. Climate is the gap.

---

<!-- _class: chart -->

Walloon wheat: observed vs trend.

![w:920](../../pictures/presentations/detrend-en.png)

---

<!-- _class: full -->

![bg brightness:0.38](../../pictures/presentations/photos/rain.png)

# Wheat × rain
# ρ ≈ −0.68

Spearman on the residual. Small n. Ranks.

---

<!-- _class: chart -->

The five clearest signals.

![w:980](../../pictures/presentations/ranking-en.png)

---

<!-- _class: split -->

![bg left:40%](../../pictures/presentations/photos/hills.png)

# No pooling.

Same sign everywhere. Provinces are not independent draws.

![w:480](../../pictures/presentations/map-en.png)

---

<!-- _class: chart -->

Why not XGBoost? n = 14–25. A line + leave-one-year-out.

![w:640](../../pictures/presentations/mae-en.png)

---

<!-- _class: dark -->

# Where it breaks.

One ERA5 point per province.

One April–September calendar.

Correlation ≠ cause.

No CMIP6 scenario.

---

<!-- _class: cta -->

![bg brightness:0.30](../../pictures/presentations/photos/explore.png)

# Reproduce.

[Explore online](../explore-en.html)

`python -m agri_climat run`

`python -m agri_climat dashboard`

Python · scikit-learn · Streamlit
