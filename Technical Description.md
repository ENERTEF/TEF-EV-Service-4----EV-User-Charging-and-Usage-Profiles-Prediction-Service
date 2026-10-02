TEF_EV-EV_USER_CHARGING_PROFILES
================================

**EV-user charging and usage profiles prediction for residential smart charging**

Overview (version 1.0)
----------------------

**TEF_EV-EV_USER_CHARGING_PROFILES** predicts when, how much and for how long residential EV users
charge, so an aggregator or DSO can plan flexible home charging. It is built on four real Irish
households (ESB Networks Dingle Electrification Project: 2.1 kWp PV, 5 kWh battery, Hyundai Kona
Electric, 7.4 kW Wallbox) — 738 charging sessions, 18,603 journeys, February 2021 → January 2022.

Two self-contained notebooks implement the service and a third tests it on external data; they
depend only on `requirements.txt` (the model libraries are **pinned**, see *How to run*):

*   **`EV_Charging_Analysis.ipynb`** — the analysis and research record: data quality and outages,
    charging behaviour and profiles, three prediction heads evaluated walk-forward, the physical
    closure between driving and charging, and the counterfactual value of smart charging.

*   **`EV_Session_Energy_Model.ipynb`** — the deployed model: session-energy prediction with
    uncertainty bands, the algorithm selection, and the exported model with its Hugging Face card.

*   **`EV_External_Validation.ipynb`** — external validation on open data (a Renault Zoe
    data-logger and 35,377 Norwegian residential sessions) and a check of the results above against
    stronger no-model baselines; see *External validation*.

Implemented AI Services
-----------------------

### Charging-event, volume and window prediction (analysis notebook)

*   **Head A — will-charge probability** (day level): pooled ROC-AUC 0.66, PR-AUC 0.63 (base rate
    0.50), calibrated (Brier skill 0.13). The pooled score flatters: a household's own charge rate
    alone gives 0.63, and 89 % of the lowest-probability quintile is one household (30–68 % of days
    across the four). Within a household the model reaches AUC 0.62 against 0.45–0.47 for
    persistence, recency and the base rate, and the quintile spread is 37 % against 61 % of days
    (pooled: 29 % against 68 %) — a real but modest need-to-charge signal.

*   **Head B — energy volume:** nMAE falls from ~103 % at one day to 33 % at fourteen days per
    household, and to 20 % pooled across the four households. A trailing 28-day average of the
    household's own energy falls as far (~105 % to 27 %; 15 % pooled) and is as good or better
    beyond one day, so the fall is an aggregation effect, not skill of the model. **Session
    energy** (walk-forward) is where it adds skill: MAE 12.5 kWh against 16.0 for the training
    median and for the household's trailing median (22 % lower).

*   **Head C — connection window:** dwell-time MAE 3.65 h against a median dwell of 9.4 h and
    3.7 h of active charging — the scheduler needs the window, not the exact minute. The model
    improves on a constant window estimate only slightly: 11 % below the training median (4.10 h)
    and 13 % below the household's trailing median (4.20 h).

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

| Metric | Model (GBR) | Distance baseline (× 0.18 kWh/km) | Constant (training median) |
|---|---|---|---|
| MAE | 10.46 kWh | 18.72 kWh | 14.85 kWh |
| RMSE | 14.20 kWh | 25.88 kWh | 18.45 kWh |
| q10–q90 coverage | 79.6 % | 36.1 % | 87.8 % |

The model cuts the error by 44 % against the distance baseline and its uncertainty band holds its
nominal 80 % coverage; per household the MAE is 8.4–11.4 kWh against 13.6–21.3 kWh for the
baseline. The distance rule is a weak yardstick (a constant beats it): against the best no-model
reference, a constant training median, the cut is **30 %** (95 % interval of the MAE gap
2.8–6.0 kWh) — real and significant, but smaller than the headline. The household's trailing
median of its last five sessions scores 15.23 kWh.

External validation
-------------------

`EV_External_Validation.ipynb` downloads two open data sets from Zenodo (CC-BY-4.0, MD5-verified)
and reproduces the published hold-out exactly with the shipped model before using it.

*   **Renault Zoe data-logger** ([Zenodo 7033914](https://zenodo.org/records/7033914), the only open
    set found that links driving and charging on one vehicle): 62 sessions from two cars (22 and
    37 kWh packs), 41 with a verified-complete context. Zero-shot, the deployed model's MAE is 5.19 kWh
    against 4.42 for the distance baseline on all sessions and 3.67 against 3.98 on the verified
    subset; both 95 % intervals include zero, and the sign differs between the two subsets
    (stable within each across extraction settings). On normal sessions it ties the baseline
    (4.5 against 4.4 kWh); it loses on the 8 sessions more than 400 h after the previous one
    (10.1 against 4.8 kWh), a region the training data covers thinly (90th percentile ≈ 100 h).
    It has no battery-capacity input. A smoke test, not a benchmark: there is no demonstrated
    transfer, and a large transfer gain is excluded.

*   **Norwegian residential sessions** ([Zenodo 13896176](https://zenodo.org/records/13896176),
    35,377 measured sessions, 267 users, 12 sites; no driving data, so the heads are refitted on
    reduced features): will-charge pooled AUC 0.78, within-user 0.64 (the user's own rate alone: 0.72
    pooled, 0.50 within); quantile GBR with user history MAE 4.96 kWh against 5.52 for the user's
    trailing median, q10–q90 coverage 81 % (with only the three deployed features that exist there:
    MAE 7.52, coverage 75 %); dwell MAE 7.2 h against a median dwell of 11.3 h; volume: a trailing
    28-day average matches the model at every horizon; segmentation: silhouette 0.21–0.22 for every
    k = 2–6, no clear structure.

The same notebook (§5) and the analysis notebook (§9–§11) also check the pilot's own results
against no-model baselines; those are the figures quoted for the heads and in *Results* above.

Outputs (version 1.0)
---------------------

*   Trained model `Data/models/session_energy.joblib` (q10 / q50 / q90), for Hugging Face as
    [`EnerTEF/EV-Service4-User-Charging-and-Usage-Profiles-Prediction`](https://huggingface.co/EnerTEF/EV-Service4-User-Charging-and-Usage-Profiles-Prediction)
    (upload is opt-in, `EV_Session_Energy_Model.ipynb` §8), with `metrics.json`, `benchmark.json`,
    the pinned `requirements.txt`, the `LICENSE` and the model card (`README.md`) in `Data/models/`.
    Following the EnerTEF upload guidelines the package also carries a short script, `example.py`,
    that loads a small open sample data set, `example_sessions.csv` (62 Renault Zoe sessions from
    [Zenodo 7033914](https://zenodo.org/records/7033914), CC-BY-4.0, no timestamps; the pilot's
    training data is restricted and cannot be shared), and runs the model on it. The sample is out
    of domain: it shows how to run the model, not how accurate it is.

*   Analysis artefacts (daily panel, sessions, calibration, volume by horizon, profiles) and
    figures in `outputs/` (regenerated by the analysis notebook, git-ignored)

How to run
----------

```bash
py -3.11 -m venv .venv            # Python 3.11 (3.12 also works; 3.13 is not supported)
.venv\Scripts\activate            # macOS / Linux: python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
jupyter lab                       # open a notebook and run all cells from the repository root
```

The model libraries are **pinned** in `requirements.txt` (Python 3.11.9 · numpy 1.26.4 ·
pandas 2.2.3 · scikit-learn 1.5.2 · lightgbm 4.5.0 · xgboost 2.1.3 · joblib 1.4.2). The published
`session_energy.joblib` is a pickle: it **does not load on scikit-learn 1.6 or newer**, and the
session notebook refuses to run or export on another release. The analysis and session notebooks
run in under a minute once the dataset is in `Data/`; the validation notebook downloads about
125 MB from Zenodo on first run and takes about five minutes. Publishing to Hugging Face
(`EV_Session_Energy_Model.ipynb` §8) is opt-in and needs a token that may write to the EnerTEF
organisation (`hf auth login`; a fine-grained token must list EnerTEF under *Org permissions*). The
cell checks the token first, creates a missing repo as private, and explains any missing permission.

Limitations and next steps
--------------------------

*   Four households only: a demonstrator, not a general-purpose predictor. No transfer to another
    vehicle is demonstrated (see *External validation*).

*   The session-energy model has no battery-capacity input and covers very long gaps since the
    last charge thinly; its 44 % headline is against a weak baseline, the gain over the best
    no-model reference is 30 %.

*   Day-level charging timing (Head A) sits close to its noise floor; most of the pooled ranking
    is which household it is. Within a household the signal is real but modest.

*   The volume head has no demonstrated skill over a trailing 28-day average, and the window head
    only a slight one; session energy is the head that clearly beats its no-model reference.

*   Whether and when a session starts is outside the session-energy model; the three heads
    together form the service's output contract.

*   Next steps are data more than algorithms: more households and vehicles (the algorithm
    bake-off is within seed noise), pack size or state of charge as an input, and a second site
    for a proper external test.
