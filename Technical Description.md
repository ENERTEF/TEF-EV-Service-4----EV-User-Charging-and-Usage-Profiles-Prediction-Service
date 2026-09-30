TEF_EV-EV_USER_CHARGING_PROFILES
================================

**EV-user charging and usage profiles prediction for residential smart charging**

Overview (version 1.0)
----------------------

**TEF_EV-EV_USER_CHARGING_PROFILES** predicts when, how much and for how long residential EV users
charge, so an aggregator or DSO can plan flexible home charging. It is built on four real Irish
households (ESB Networks Dingle Electrification Project: 2.1 kWp PV, 5 kWh battery, Hyundai Kona
Electric, 7.4 kW Wallbox) — 738 charging sessions, 18,603 journeys, February 2021 → January 2022.

Two self-contained notebooks implement the service; they depend only on `requirements.txt`:

*   **`EV_Charging_Analysis.ipynb`** — the analysis and research record: data quality and outages,
    charging behaviour and profiles, three prediction heads evaluated walk-forward, the physical
    closure between driving and charging, and the counterfactual value of smart charging.

*   **`EV_Session_Energy_Model.ipynb`** — the deployed model: session-energy prediction with
    uncertainty bands, the algorithm selection, and the exported model with its Hugging Face card.

Implemented AI Services
-----------------------

### Charging-event, volume and window prediction (analysis notebook)

*   **Head A — will-charge probability** (day level): ROC-AUC 0.66, PR-AUC 0.63 (base rate 0.50),
    calibrated (Brier skill 0.13). Users in the lowest-probability quintile charge on 29 % of days,
    in the highest on 68 % — a usable ranking for selecting addressable users.

*   **Head B — energy volume:** nMAE falls from ~103 % at one day to 33 % at fourteen days per
    household, and to 20 % pooled across the four households.

*   **Head C — connection window:** dwell-time MAE 3.65 h against a median dwell of 9.4 h and
    3.7 h of active charging — the scheduler needs the window, not the exact minute.

### Session-energy model (model notebook)

*   **Target:** energy delivered by a home charging session (kWh), predicted when the session
    starts, at the q10 / q50 / q90 quantiles.

*   **Features (7, leakage-safe):** distance driven since the previous session, trips earlier that
    day, hours since the last charge, tariff band at the start (household price terciles), PV
    generated since midnight, hour of day, weekend flag — all rebuilt from data strictly before the
    session start.

*   **Split:** chronological — the earliest 587 sessions train, the most recent 147 are held out.

Algorithm selection
-------------------

scikit-learn `GradientBoostingRegressor` (the incumbent), **LightGBM** and **XGBoost** were
compared on the same sessions and split, with the same capacity translated to each library
(200 trees, depth 3, learning rate 0.05, minimum leaf 25, row subsampling 0.85), no per-library
tuning, and three seeds. The rule was **fixed before the experiment**: a challenger replaces GBR
only if its q50 MAE is at least 3 % lower, the gap exceeds the seed-to-seed range, and its q10–q90
coverage drops by at most 5 points.

| Algorithm | Hold-out q50 MAE (kWh), mean [min–max] | q10–q90 coverage | Verdict |
|---|---|---|---|
| scikit-learn GBR | 10.38 [10.29–10.46] | 80.3 % | **retained** |
| LightGBM | 10.36 [10.34–10.38] | 79.8 % | rejected — +0.2 %, within seed noise |
| XGBoost | 10.28 [10.20–10.33] | 80.1 % | rejected — +1.0 %, within seed noise |

All three are within about 1 % of each other, inside the noise from the seed alone: with 587
training sessions and 7 features, the library is not the limiting factor — more sessions and
richer context are. Per-seed results: `Data/models/benchmark.json`.

Data Sources
------------

*   **Residential Energy Dataset with Electric Vehicles, Photovoltaic Generation and Tariff
    Variability in Ireland** — Avgoloupis, D. *et al.*, Scientific Data 13:834 (2026),
    [doi:10.1038/s41597-026-07186-3](https://doi.org/10.1038/s41597-026-07186-3): journeys and
    charging events (`JourneyCharge/`), 30-minute solar generation and electricity price
    (`EnergyStreams/`), daily Open-Meteo weather.

*   The dataset describes four real households and is **not redistributed in this repository**.
    Obtain it via the data paper and place it under `Data/` (git-ignored), or set
    `DINGLE_DATASET_ROOT`.

Results (version 1.0)
---------------------

Session-energy model, 147 held-out sessions (24 Nov 2021 → 30 Jan 2022):

| Metric | Model (GBR) | Baseline (distance × 0.18 kWh/km) |
|---|---|---|
| MAE | 10.46 kWh | 18.72 kWh |
| RMSE | 14.20 kWh | 25.88 kWh |
| q10–q90 coverage | 79.6 % | 36.1 % |

The model cuts the error by 44 % and its uncertainty band holds its nominal 80 % coverage;
per household the MAE is 8.4–11.4 kWh against 13.6–21.3 kWh for the baseline.

Outputs (version 1.0)
---------------------

*   Trained model `Data/models/session_energy.joblib` (q10 / q50 / q90), published on Hugging Face
    as [`EnerTEF/Service4-SessionEnergy`](https://huggingface.co/EnerTEF/Service4-SessionEnergy),
    with `metrics.json`, `benchmark.json` and the model card (`README.md`) in `Data/models/`

*   Analysis artefacts (daily panel, sessions, calibration, volume by horizon, profiles) and
    figures in `outputs/` (regenerated by the analysis notebook, git-ignored)

How to run
----------

```bash
python -m venv .venv
.venv\Scripts\activate            # macOS / Linux: source .venv/bin/activate
pip install -r requirements.txt
jupyter lab                       # open either notebook and run all cells from the repository root
```

Each notebook runs in under a minute once the dataset is in `Data/`. Publishing to Hugging Face
(`EV_Session_Energy_Model.ipynb` §8) is opt-in and needs a write token (`hf auth login`).

Limitations and next steps
--------------------------

*   Four households only: a demonstrator, not a general-purpose predictor.

*   Day-level charging timing (Head A) sits close to its noise floor; the ranking, not the
    individual prediction, is what is actionable.

*   Whether and when a session starts is outside the session-energy model; the three heads
    together form the service's output contract.
