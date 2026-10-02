---
license: mit
language:
- en
library_name: scikit-learn
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

## Model description

Predicts the **energy a home charging session will deliver** (kWh) at the q10 / q50 / q90 quantiles,
from context available just before the session: recent driving, time since the last charge, the tariff
band and the PV generated that day. Built for the EnerTEF TEF-EV EV-user charging and usage profiles
prediction service (D2.2 §2.5.4); downstream smart charging gets a point estimate and an uncertainty band.

| Field | Value |
|---|---|
| Algorithm | scikit-learn GBR — 3 quantile regressors (q10 / q50 / q90), chosen by the bake-off below |
| Parameters | `{"loss": "quantile", "init": "zero", "n_estimators": 200, "max_depth": 3, "learning_rate": 0.05, "min_samples_leaf": 25, "subsample": 0.85, "random_state": 42}` |
| Training sessions | 587 (chronologically earliest 80 %, four households) |
| Held-out sessions | 147 (most recent 20 %) |
| Version | 1.0.0 (2026-10-02) |

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

## Repository contents

| File | Content |
|---|---|
| `session_energy.joblib` | dict with `features` (order), `tariff_ordinal`, `quantiles` (`q10`/`q50`/`q90` estimators) and metadata |
| `example.py` | short script: loads the sample data and runs the model (see *Installation and inference*) |
| `example_sessions.csv` | small open sample data set (see *Inputs and data*) |
| `requirements.txt` | the pinned environment in which the model loads |
| `metrics.json` | hold-out metrics vs the baseline, split, parameters, library versions |
| `benchmark.json` | algorithm bake-off: per-seed results, rule, verdicts |
| `LICENSE` | MIT licence of the model and code (the sample data keeps its own licence, below) |

## Inputs and data

### Training data (restricted, not included)

**Residential energy dataset with electric vehicles, PV generation and tariff variability in Ireland** —
annotated EV home-charging sessions, journeys, household energy streams, PV generation and tariff data
for four "ambassador" households (`id01`–`id04`) of the ESB Networks Dingle Electrification Project.

Avgoloupis, D. et al. Residential Energy Dataset with Electric Vehicles, Photovoltaic Generation and Tariff Variability in Ireland. Scientific Data 13:834 (2026). https://doi.org/10.1038/s41597-026-07186-3

**The dataset is not redistributed here.** It describes four real households, so it stays with its owners;
household identifiers are pseudonymous — do not attempt re-identification. Obtain it via the data paper.

### Sample data (open): `example_sessions.csv`

62 charging sessions of two cars from an open data-logger data set: Morea, Alessandrini & Spadaro,
*Electric car parameters over 29 months* (Area Science Park, 2022,
[doi:10.5281/zenodo.7033914](https://doi.org/10.5281/zenodo.7033914), **CC-BY-4.0** — the sample keeps that licence and
attribution). It was converted to this model's input schema by the notebook `EV_External_Validation.ipynb` (§3.7) of the project
repository; timestamps are removed.

| Column | Meaning |
|---|---|
| `session`, `vehicle` | session id; car `A` (about 22 kWh pack) or car `B` (about 37 kWh pack) |
| the 7 features | exactly as above, in model order; `tariff_ordinal` is 2 (unknown) and `pv_today_kwh` is 0 in every row because the logger records neither |
| `energy_kwh` | measured energy of the session, **battery side** (state-of-charge gain × pack size; the training target is measured at the wallbox) |
| `context_verified` | `True` for the 41 sessions whose pre-session context was checked complete (odometer and state-of-charge continuity) |

The sample is **out of domain** (other cars, mostly short morning top-ups, a different charging context): it shows how to load
and run the model, not how accurate it is (see *How good is it?*).

## Installation and inference

### Requirements

`session_energy.joblib` is a pickle: it **only loads on the scikit-learn release that wrote it (1.5.2)** and fails on 1.6 / 1.7 with
`AttributeError: Can't get attribute '__pyx_unpickle_CyPinballLoss'`. Use Python 3.11 (3.9–3.12 have wheels) and the pins in `requirements.txt`:

```
scikit-learn==1.5.2
numpy==1.26.4
pandas==2.2.3
joblib==1.4.2
```

### Run the bundled example

```bash
pip install -r requirements.txt
python example.py
```

It prints the q10 / q50 / q90 prediction of the first sessions and the error against the project's distance baseline. The last lines
are:

```
all sessions      n= 62 | model MAE 5.19 kWh | distance baseline MAE 4.42 | q10-q90 coverage 87 %
context verified  n= 41 | model MAE 3.67 kWh | distance baseline MAE 3.98 | q10-q90 coverage 93 %
```

### Predict one session

```python
import joblib
import numpy as np
import sklearn

assert sklearn.__version__ == "1.5.2", "session_energy.joblib needs scikit-learn 1.5.2 (see Requirements)"
bundle = joblib.load("session_energy.joblib")
# Feature order: recent_trip_km, trips_today, hours_since_last_charge, tariff_ordinal,
#                pv_today_kwh, hour_of_day, is_weekend
x = [[12.5, 2.0, 8.0, 0.0, 0.0, 18.5, 0.0]]
lo, mid, hi = np.sort([est.predict(x)[0] for est in bundle["quantiles"].values()])
# the model has no battery-capacity input: clip to the pack size of the vehicle (kWh)
lo, mid, hi = (min(v, 64.0) for v in (lo, mid, hi))   # 64 kWh = the pilot's Hyundai Kona
```

## Evaluation

### Hold-out accuracy (pilot households)

| Metric | scikit-learn GBR | Distance baseline¹ | Constant (training median) |
|---|---|---|---|
| MAE (kWh) | 10.46 | 18.72 | 14.85 |
| RMSE (kWh) | 14.20 | 25.88 | 18.45 |
| q10–q90 coverage | 79.6 % | 36.1 % | 87.8 % |

MAE is 44 % lower than the distance baseline, but the distance rule is a weak yardstick (a constant beats it):
against the best no-model reference (14.85 kWh, a constant training median) it is **30 % lower**.
The constant's q10–q90 band is the training quantiles, which over-cover.

¹ The project's no-model rule: distance since the previous session × 0.18 kWh/km, plus 5 % per trip beyond the first that day, clamped to 1–80 kWh.

### How good is it?

A demonstrator that learns something real about session size inside its own four households — not a validated general predictor.

- **In-domain, real but modest in absolute terms:** MAE 10.5 kWh on held-out sessions averaging 28.6 kWh; the q10–q90 band holds close to its nominal 80 % (79.6 %).
- **No demonstrated transfer.** On a different vehicle (the 62 sessions of the open sample above) its MAE was 5.2 kWh against 4.4 kWh for the distance baseline on all sessions, and 3.7 against 4.0 on the 41 sessions with a verified-complete context; both differences are within noise (95 % intervals include zero). A small, heterogeneous sample, so a smoke test, not a benchmark (notebook `EV_External_Validation.ipynb`).
- **No battery-capacity input:** it can predict more energy than a pack holds. Clip to the pack size of the vehicle you predict for.
- **Weak after long gaps:** sessions more than ~400 h after the previous one are poorly covered by the training data (its 90th percentile is ~100 h) and were badly under-predicted out of domain.
- **Data, not algorithm, is the limit:** LightGBM and XGBoost are within seed noise of the selected model (below).

### Model selection — why scikit-learn GBR

scikit-learn GBR (the incumbent), LightGBM and XGBoost were trained on the same sessions and split, with
the same capacity translated to each library and no per-library tuning, over three seeds. The rule was
fixed before the run: a challenger replaces GBR only if its q50 MAE is at least 3 % lower,
the gap exceeds the seed-to-seed range, and its q10–q90 coverage drops by at most 5 points.

| Algorithm | Hold-out q50 MAE (kWh), mean [min–max] | q10–q90 coverage | Fit time (3 quantiles) | Verdict |
|---|---|---|---|---|
| scikit-learn GBR | 10.38 [10.29–10.46] | 80.3 % | 1.1 s | incumbent — **selected** |
| LightGBM | 10.36 [10.34–10.38] | 79.8 % | 0.1 s | rejected — MAE gain +0.2 % is below the 3 % bar; gap is within the 1.7 % seed-to-seed range |
| XGBoost | 10.28 [10.20–10.33] | 80.1 % | 0.3 s | rejected — MAE gain +1.0 % is below the 3 % bar; gap is within the 1.7 % seed-to-seed range |

MAE over seeds 42, 43, 44.

**scikit-learn GBR is retained** — no challenger cleared the rule.

Per-seed results: `benchmark.json`.

## Reproduce the workflow

The model, its bake-off and this card are produced by `EV_Session_Energy_Model.ipynb` in the project repository
([TEF-EV-Service-4----EV-User-Charging-and-Usage-Profiles-Prediction-Service](https://github.com/ENERTEF/TEF-EV-Service-4----EV-User-Charging-and-Usage-Profiles-Prediction-Service)); `EV_Charging_Analysis.ipynb` holds the analysis behind the service and
`EV_External_Validation.ipynb` the external validation. The first two need the restricted training data; the validation notebook
downloads open data. Use Python 3.11 and the repository's pinned `requirements.txt`.

## Intended uses and limitations

**Intended use:** research and demonstration of smart-charging inputs for residential home charging — an energy estimate with an
uncertainty band for a session that is about to start. **Not intended for:** billing, safety-critical or grid-operational control,
vehicles or charging contexts unlike the pilot's, or predicting whether or when a session starts.

- Four households only (587 training sessions): a demonstrator, not a general-purpose predictor.
- No demonstrated transfer to other vehicles or usage, and no battery-capacity input (see *How good is it?*).
- Poorly covered: very long gaps since the last charge.
- The q10–q90 band is empirical; its coverage is reported above against a nominal 80 %.
- Whether and when a session starts is a separate question, not answered by this model.
- Needs scikit-learn 1.5.2 exactly (see *Requirements*).

## License and project references

Model and code: MIT (`LICENSE`). Sample data: CC-BY-4.0 (Morea et al., above). Part of the EnerTEF project
([huggingface.co/EnerTEF](https://huggingface.co/EnerTEF)), TEF-EV node, Service 4 (EV-user charging and usage profiles
prediction, D2.2 §2.5.4). Code and the full experiment: [TEF-EV-Service-4----EV-User-Charging-and-Usage-Profiles-Prediction-Service](https://github.com/ENERTEF/TEF-EV-Service-4----EV-User-Charging-and-Usage-Profiles-Prediction-Service).

## Citation

Training data: Avgoloupis, D. et al. Residential Energy Dataset with Electric Vehicles, Photovoltaic Generation and Tariff Variability in Ireland. Scientific Data 13:834 (2026). https://doi.org/10.1038/s41597-026-07186-3

Sample data: Morea, F., Alessandrini, S., Spadaro, M. Electric car parameters over 29 months. Area Science Park (2022). Zenodo. https://doi.org/10.5281/zenodo.7033914 (CC-BY-4.0)
