---
library_name: scikit-learn
license: mit
pipeline_tag: tabular-regression
tags:
- energy
- ev-charging
- smart-charging
- quantile-regression
- gradient-boosting
- enertef
---

# Service 4 — residential EV session energy (quantile gradient boosting)

Predicts the **energy a home charging session will deliver** (kWh) at the q10 / q50 / q90 quantiles,
from context available just before the session: recent driving, time since the last charge, the tariff
band and the PV generated that day. Built for the EnerTEF TEF-EV EV-user charging and usage profiles
prediction service (D2.2 §2.5.4); downstream smart charging gets a point estimate and an uncertainty band.

Code and the full experiment: [TEF-EV-Service-4----EV-User-Charging-and-Usage-Profiles-Prediction-Service](https://github.com/ENERTEF/TEF-EV-Service-4----EV-User-Charging-and-Usage-Profiles-Prediction-Service) (notebook `EV_Session_Energy_Model.ipynb`).

## Model

| Field | Value |
|---|---|
| Algorithm | scikit-learn GBR — 3 quantile regressors (q10 / q50 / q90), chosen by the bake-off below |
| Parameters | `{"loss": "quantile", "init": "zero", "n_estimators": 200, "max_depth": 3, "learning_rate": 0.05, "min_samples_leaf": 25, "subsample": 0.85, "random_state": 42}` |
| Training sessions | 587 (chronologically earliest 80 %, four households) |
| Held-out sessions | 147 (most recent 20 %) |
| Version | 1.0.0 (2026-09-30) |

### Features (order matters)

| Feature | Meaning |
|---|---|
| `recent_trip_km` | Distance driven since the previous session ended (km). |
| `trips_today` | Journeys started earlier on the session day. |
| `hours_since_last_charge` | Hours since the previous session ended. |
| `tariff_ordinal` | Tariff band at the session start: off-peak 0, shoulder 1, standard 2 (unknown), peak 3. |
| `pv_today_kwh` | PV generated since midnight (kWh). |
| `hour_of_day` | Fractional hour of the session start (UTC). |
| `is_weekend` | 1 on Saturday / Sunday, else 0. |

## Hold-out accuracy

| Metric | scikit-learn GBR | Baseline (distance × 0.18 kWh/km) |
|---|---|---|
| MAE (kWh) | 10.46 | 18.72 |
| RMSE (kWh) | 14.20 | 25.88 |
| q10–q90 coverage | 79.6 % | 36.1 % |

Four Irish households only — no generalisation beyond them is claimed.

## Model selection — why scikit-learn GBR

scikit-learn GBR (the incumbent), LightGBM and XGBoost were trained on the same sessions and split, with
the same capacity translated to each library and no per-library tuning, over three seeds. The rule was
fixed before the run: a challenger replaces GBR only if its q50 MAE is at least 3 % lower,
the gap exceeds the seed-to-seed range, and its q10–q90 coverage drops by at most 5 points.

| Algorithm | Hold-out q50 MAE (kWh), mean [min–max] | q10–q90 coverage | Fit time (3 quantiles) | Verdict |
|---|---|---|---|---|
| scikit-learn GBR | 10.38 [10.29–10.46] | 80.3 % | 1.1 s | incumbent — **selected** |
| LightGBM | 10.36 [10.34–10.38] | 79.8 % | 0.1 s | rejected — MAE gain +0.2 % is below the 3 % bar; gap is within the 1.7 % seed-to-seed range |
| XGBoost | 10.28 [10.20–10.33] | 80.1 % | 0.4 s | rejected — MAE gain +1.0 % is below the 3 % bar; gap is within the 1.7 % seed-to-seed range |

MAE over seeds 42, 43, 44.

**scikit-learn GBR is retained** — no challenger cleared the rule.

Per-seed results: `benchmark.json`.

## Files

| File | Content |
|---|---|
| `session_energy.joblib` | dict with `features` (order), `tariff_ordinal`, `quantiles` (`q10`/`q50`/`q90` estimators) and metadata |
| `metrics.json` | hold-out metrics vs the baseline, split, parameters, library versions |
| `benchmark.json` | algorithm bake-off: per-seed results, rule, verdicts |

## Usage

```python
import joblib
import numpy as np

bundle = joblib.load("session_energy.joblib")
# Feature order: recent_trip_km, trips_today, hours_since_last_charge, tariff_ordinal,
#                pv_today_kwh, hour_of_day, is_weekend
x = [[12.5, 2.0, 8.0, 0.0, 0.0, 18.5, 0.0]]
lo, mid, hi = np.sort([est.predict(x)[0] for est in bundle["quantiles"].values()])
```

## Data

**Residential energy dataset with electric vehicles, PV generation and tariff variability in Ireland** —
annotated EV home-charging sessions, journeys, household energy streams, PV generation and tariff data
for four "ambassador" households (`id01`–`id04`) of the ESB Networks Dingle Electrification Project.

Avgoloupis, D. et al. Residential Energy Dataset with Electric Vehicles, Photovoltaic Generation and Tariff Variability in Ireland. Scientific Data 13:834 (2026). https://doi.org/10.1038/s41597-026-07186-3

**The dataset is not redistributed here.** It describes four real households, so it stays with its owners;
household identifiers are pseudonymous — do not attempt re-identification. Obtain it via the data paper.

## Limitations

- Four households only: a demonstrator, not a general-purpose predictor.
- The q10–q90 band is empirical; its coverage is reported above against a nominal 80 %.
- Whether and when a session starts is a separate question, not answered by this model.

## Citation

Avgoloupis, D. et al. Residential Energy Dataset with Electric Vehicles, Photovoltaic Generation and Tariff Variability in Ireland. Scientific Data 13:834 (2026). https://doi.org/10.1038/s41597-026-07186-3
