# EV-User Charging and Usage Profiles Prediction Service

**Service:** EV-User Charging and Usage Profiles Prediction Service  
**Service ID:** Service4  
**Version:** 1.0  
**Service Provider:**  
**Document Type:** Technical Manual & Service Specification  

---

# Overview

The **EV-User Charging and Usage Profiles Prediction Service** provides **day-ahead forecasts of charging behavior and energy demand patterns** for private and public electric vehicle (EV) users.

The service leverages:

- historical charging and usage data
- contextual information such as location and time-of-day
- anonymized user demographics and behavioral patterns
- exogenous variables such as weather and traffic conditions

It predicts:

- **when** EV users are likely to charge
- **where** charging is likely to take place
- **how much** energy they are likely to consume

Accurate and reliable predictions of EV charging patterns are critical for:

- grid stability
- efficient energy resource allocation
- charging infrastructure planning
- smart charging strategy design
- flexibility market participation
- demand response program optimization

Distribution System Operators (DSOs) can use these forecasts for:

- peak shaving
- infrastructure upgrade planning
- congestion prevention
- operational load balancing

Aggregators can use them to:

- engage EV users in flexibility markets
- design demand response offers
- optimize charging coordination
- improve targeting of incentives

---

# 1. Business Context & Definitions

| Term | Definition |
|---|---|
| **EV User / Vehicle ID** | Unique identifier for an electric vehicle or EV owner participating in the charging network, typically pseudonymized or anonymized |
| **Charging Session** | A discrete event during which an EV is connected to an EVSE and draws energy |
| **Timestamp** | Date and time at which measurements or forecasts apply, typically aligned to 15-minute intervals |
| **Energy Demand** | Total electrical energy drawn from the grid by EV charging infrastructure over a specified period |
| **Contextual Data** | Environmental and situational variables influencing charging behavior, such as weather, traffic, local events, and calendar effects |
| **Forecast Horizon** | Time window ahead for which charging behavior is predicted |
| **Resolution / Granularity** | Temporal and spatial resolution of the forecasts |
| **User Segmentation** | Categorization of EV users into behavioral groups based on historical usage patterns |

---

## 1.1 DSO and Aggregator Context

This service is designed for:

- **Distribution System Operators (DSOs)**
- **Aggregators / system operators**

These stakeholders manage EV charging infrastructure and require forecasting capabilities to optimize operations, customer engagement, and grid stability.

In day-to-day operations, forecast outputs help them to:

- anticipate peak charging demand periods
- plan charging infrastructure investments
- schedule maintenance
- design tariffs and incentive programs
- proactively balance demand
- reduce congestion and transformer overloading risks

The service provider supplies:

- historical charging usage data
- anonymized user demographic and behavioral data
- smart meter telemetry
- EVSE operational data

DSOs and aggregators remain responsible for:

- operational decisions
- grid management
- safety obligations
- regulatory compliance

Operationally, the service supports:

- on-demand forecast updates via API calls
- scheduled batch processing
- forecast refreshes when new data becomes available
- forecast refreshes when contextual conditions change

---

# 2. Problem Statement

The objective is to deliver a **reliable, production-grade service** that predicts EV charging behavior and energy demand across both **private and public charging infrastructure**.

The service must support:

- **individual user-level predictions**
- **aggregated charging point, station-level, or regional forecasts**

The service shall expose an authenticated API for requesting forecasts for:

- specific time ranges
- locations
- user segments
- requested aggregation levels

Forecasts must be generated:

- on demand
- or on a schedule

Response times must be suitable for **operational use**.

The forecasting approach combines:

- historical charging session data
- user behavioral patterns
- smart meter and EVSE operational signals
- weather forecasts
- traffic conditions
- calendar effects such as holidays and special events

Machine learning models are expected to capture:

- temporal patterns
- user segmentation
- contextual influences on charging behavior
- usage variability across locations and charging modes

---

# 3. Data Description

## 3.1 Data Requirements & Sources

The service requires access to the following data sources.

### A. Smart Meter and EVSE Data (Private, Internal)

Historical charging session records including:

- timestamp
- charging point identifier
- anonymized vehicle ID
- energy consumed (kWh)
- charging duration
- session start and end times

Additional operational metrics may include:

- charge rate (kW)
- state of charge
- charging mode (AC/DC)

---

### B. User Demographic and Behavioral Data (Anonymized, Internal)

Pseudonymized user profiles describing behavioral patterns without exposing personally identifiable information.

Typical features may include:

- user segment classification
- preferred charging locations
- typical charging times
- historical charging frequency
- public vs private charging preference

Example user segments:

- commuter
- frequent charger
- opportunistic user

---

### C. Weather Forecast and Traffic Data (Public APIs)

Contextual environmental data may include:

- temperature
- precipitation
- wind speed
- forecasted weather conditions

Traffic-related data may include:

- congestion levels
- commute patterns
- public event schedules

Example public sources may include:

- Open Meteo
- traffic and event APIs

---

## 3.2 Data Dictionary – Charging Session Records

| Variable | Variable name | Type | Measurement unit | Description | Allowed values / Examples |
|---|---|---|---|---|---|
| Date | `date` | Date | YYYY-MM-DD | Date of charging session | 2024-01-15 |
| Timestamp Start | `timestamp_start` | Timestamp | YYYY-MM-DD HH:MM:SS | Session start timestamp | 2024-01-15 08:30:00 |
| Timestamp End | `timestamp_end` | Timestamp | YYYY-MM-DD HH:MM:SS | Session end timestamp | 2024-01-15 10:45:00 |
| Vehicle ID | `vehicle_id` | String | - | Anonymized vehicle/user identifier | VEH_A3F9D2 |
| Charging Point ID | `charging_point_id` | String | - | Unique identifier for EVSE location | CP_SITE_042 |
| Energy Consumed | `energy_kwh` | Numeric | kWh | Total energy delivered during session | 25.4 |
| Charging Duration | `duration_minutes` | Numeric | minutes | Total session duration | 135 |
| Average Power | `avg_power_kw` | Numeric | kW | Average charging power | 11.2 |
| Peak Power | `peak_power_kw` | Numeric | kW | Peak charging power during session | 22.0 |
| State of Charge Initial | `soc_initial` | Numeric | % | Battery state at session start | 25 |
| State of Charge Final | `soc_final` | Numeric | % | Battery state at session end | 80 |
| Charging Mode | `charging_mode` | Categorical | - | AC or DC charging | AC / DC |
| Location Type | `location_type` | Categorical | - | Charging environment type | Public / Workplace / Residential |
| User Segment | `user_segment` | Categorical | - | Behavioral classification | Commuter / Frequent / Opportunistic |

---

## 3.3 Data Dictionary – Contextual Variables

| Variable | Variable name | Type | Measurement unit | Description | Allowed values / Examples |
|---|---|---|---|---|---|
| Temperature | `temperature` | Numeric | °C | Ambient temperature | 15.3 |
| Precipitation | `precipitation` | Numeric | mm/h | Rainfall intensity | 0.5 |
| Wind Speed | `wind_speed` | Numeric | m/s | Wind speed | 3.2 |
| Hour of Day | `hour` | Numeric | - | Hour of day (0–23) | 14 |
| Day of Week | `day_of_week` | Categorical | - | Day of the week | Monday / Tuesday / ... |
| Is Weekend | `is_weekend` | Boolean | - | Weekend indicator | True / False |
| Is Holiday | `is_holiday` | Boolean | - | Public holiday indicator | True / False |
| Traffic Congestion | `traffic_level` | Categorical | - | Traffic congestion level | Low / Medium / High |
| Special Event | `special_event` | Boolean | - | Local event indicator | True / False |

---

## 3.4 Data Availability & Format

| Parameter | Description |
|---|---|
| **Data formats** | JSON, CSV; accessible via REST APIs or batch upload |
| **Data resolution** | Charging session data at event level; contextual data at 15-minute intervals |
| **Estimated data size** | 100,000–1,000,000 sessions per month per deployment site |
| **Documentation** | Metadata dictionaries for schemas, field definitions, and quality indicators |

---

# 4. Analytics, Scope & Update Frequency

## Temporal Scope

Forecasts cover:

- the next **24–48 hours**
- ahead of the forecast issue time

Outputs may be generated at:

- **15-minute resolution**
- **1-hour resolution**

depending on operational requirements.

---

## Update Frequency

Forecasts are generated:

- on demand via API requests
- or on a scheduled basis

Example schedules may include:

- hourly
- every 6 hours

The service supports both:

- real-time operational queries
- batch processing

---

## Forecast Output Package

For each forecast request, the service returns a structured forecast package including:

- **issue time and validity window**
- **time-indexed charging profile**
- **charging event probabilities**
- **user segmentation insights**
- **traceability metadata**

### Issue Time & Validity Window

Includes:

- timestamp (UTC) when the forecast was generated
- start and end time of the forecast horizon

### Time-Indexed Charging Profile

A time series of predicted charging demand values in:

- kWh
- or kW

Forecasts may be returned for:

- individual vehicles
- charging points
- aggregated regions

### Charging Event Probabilities

Probability estimates for the occurrence of charging sessions at specific:

- times
- locations

### User Segmentation Insights

Breakdown of predicted charging demand by behavioral group, such as:

- commuters
- frequent chargers
- opportunistic users

### Traceability Metadata

Includes:

- forecast ID
- model version
- input data sources

This supports:

- traceability
- debugging
- reproducibility

---

# 5. Evaluation Protocols & Metrics

The purpose of the evaluation is to verify that the service:

- operates reliably
- delivers consistent forecasts
- meets agreed performance standards
- performs under real-world operational conditions

---

## 5.1 Forecasting Protocol

The service shall:

- generate forecasts on demand or on schedule
- support horizons up to **24–48 hours ahead** of issue time
- only use information available at or before the issue time
- return time-aligned outputs
- include unique identifiers and minimal traceability fields
- behave consistently under repeated requests with the same configuration

Permitted inputs include, for example:

- historical charging sessions up to issue time
- weather forecasts valid for the target period
- available traffic and contextual signals

Minimum traceability fields include:

- model version
- input data sources

---

## 5.2 Data Gaps and Exceptions

Time periods with:

- missing
- invalid
- incomplete

charging session records shall be flagged and excluded from evaluation metrics where appropriate.

If insufficient recent data is available to produce a reliable forecast, such as for:

- a new charging location
- a recently onboarded user segment
- sparse deployment history

the service shall return a clear structured response indicating:

- degraded confidence
- partial availability
- or forecast unavailability

---

## 5.3 Service Evaluation Metrics & KPIs

### Mean Absolute Error (MAE)

Mean absolute error of forecasted charging demand versus actual measured energy consumption, aggregated across:

- forecast horizons
- locations
- requested aggregation levels

---

### Root Mean Squared Error (RMSE)

Root mean squared error of forecasted demand versus actual consumption, emphasizing larger deviations.

---

### Recall on Charging Event Detection

Percentage of actual charging sessions correctly identified by the forecast.

This measures sensitivity to charging event occurrence.

---

### User Segmentation Clustering Accuracy

Quality of behavioral user classification, measured using clustering quality metrics such as:

- silhouette score
- cluster purity
- similar segmentation metrics

---

### Response Time for Inference

Time required to generate a forecast from API request submission to response delivery.

**Target:** `< 5 seconds` for on-demand queries

---

### API Availability

Percentage of forecast requests that return a valid response within the agreed service-level timeframe.

**Target:** `> 99% uptime`

---

# 6. Deliverables & Submissions

The service provider shall deliver:

- three lifecycle-aligned reports
- technical documentation
- deployment artifacts
- handover and security documentation

---

## 6.1 Deliverable Reports

### 1️⃣ Pre-Service Deliverable – Service Design & Setup Report

Submitted prior to service start, this report documents:

- service architecture
- data pipelines
- model selection rationale
- initial deployment plan
- preliminary testing results

This phase may include testing on:

- synthetic datasets
- open datasets

Indicative milestone window:

- **M5–M7**

---

### 2️⃣ Intermediate Deliverable – Interim Performance & Operations Report

Submitted at the agreed midpoint, this report provides:

- operational insights
- initial KPI results
- integration findings with private datasets
- co-creation testing results
- identified adjustments needed to improve performance
- operational challenges and mitigation actions

Indicative milestone window:

- **M8–M10**

---

### 3️⃣ Final Deliverable – Final Evaluation & Recommendations Report

Submitted at the end of the service period, this report presents:

- comprehensive evaluation results
- lessons learned
- scalability analysis
- recommendations for future enhancements
- replication guidance across additional TEF nodes

Indicative milestone:

- **M12**

---

## 6.2 Technical Specifications & Submissions

### Service Interface Documentation

Full REST API documentation should include:

- endpoints
- request/response formats
- JSON schemas
- authentication mechanisms
- rate limits
- error handling procedures

Authentication examples may include:

- API keys
- OAuth

---

### Deployment Artifacts

The service shall be deployed using a **FastAPI backend**.

Deployment may include:

- Docker containers
- scalable runtime packaging
- cloud or cluster deployment support

The provider shall specify computational resource requirements, for example:

- GPU-enabled server requirements
- RAM requirements
- storage and runtime needs

Integration with environments such as:

- LIST cluster
- AWS cloud infrastructure

should be documented where applicable.

---

### Configuration, Versioning & Handover

Documentation shall include:

- configuration parameters
- model hyperparameters
- data refresh schedules
- model versioning scheme
- handover procedures to operational teams

It should also provide instructions for:

- retraining
- model updates
- monitoring
- operational maintenance

---

### Security & Data Protection Documentation

Documentation shall describe:

- data handling practices
- access control mechanisms
- encryption standards
- anonymization procedures
- privacy-preserving handling of user data
- compliance with GDPR and other relevant data protection regulations

This includes protections for:

- data in transit
- data at rest
- user identity privacy

---

# 7. Implementation in this Repository (version 1.0)

| Path | Content |
| ---- | ------- |
| [`EV_Charging_Analysis.ipynb`](EV_Charging_Analysis.ipynb) | Analysis and research record: data quality, charging profiles, will-charge / volume / window prediction heads, physical closure, smart-charging counterfactuals |
| [`EV_Session_Energy_Model.ipynb`](EV_Session_Energy_Model.ipynb) | The deployed session-energy model: pre-session context features → algorithm selection → training → evaluation → export |
| [`EV_External_Validation.ipynb`](EV_External_Validation.ipynb) | External validation on open data (a Renault Zoe data-logger and 35,377 Norwegian residential sessions) and a check of the published results against stronger baselines — see [§7.1](#71-external-validation-and-known-limitations) |
| [`Technical Description.md`](Technical%20Description.md) | What was built, the algorithm selection and the results |
| `Data/models/` | The Hugging Face package: trained model (`.joblib`), model card, `example.py` + `example_sessions.csv` (a short run-the-model script and a small open sample data set), pinned `requirements.txt`, `LICENSE`, metrics and algorithm bake-off — for Hugging Face as [`EnerTEF/EV-Service4-User-Charging-and-Usage-Profiles-Prediction`](https://huggingface.co/EnerTEF/EV-Service4-User-Charging-and-Usage-Profiles-Prediction) (upload is opt-in, `EV_Session_Energy_Model.ipynb` §8) |
| `requirements.txt` | Python dependencies — the model libraries are **pinned** (see Quickstart) |

**Data:** the notebooks use the *Residential Energy Dataset with Electric Vehicles, Photovoltaic
Generation and Tariff Variability in Ireland* (Scientific Data 13:834, 2026,
[doi:10.1038/s41597-026-07186-3](https://doi.org/10.1038/s41597-026-07186-3)). It describes four real
households and is **not redistributed here**: obtain it via the data paper and place `JourneyCharge/`,
`EnergyStreams/` and `open_meteo_dingle*.csv` under `Data/` (git-ignored), or set `DINGLE_DATASET_ROOT`.

**Quickstart**

```bash
py -3.11 -m venv .venv            # Python 3.11 (3.12 also works; 3.13 is not supported)
.venv\Scripts\activate            # macOS / Linux: python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
jupyter lab
```

The model libraries are **pinned** to the reference run (Python 3.11.9 · numpy 1.26.4 · pandas 2.2.3 · scikit-learn 1.5.2 ·
lightgbm 4.5.0 · xgboost 2.1.3 · joblib 1.4.2). This is required, not cosmetic: the published `session_energy.joblib` is a
pickle that **does not load on scikit-learn 1.6 or newer** (`AttributeError: … __pyx_unpickle_CyPinballLoss`), and
scikit-learn 1.5.2 / numpy 1.26.4 have no wheels for Python 3.13. The session notebook refuses to run or export on another
scikit-learn release. `pip install -r requirements.txt` was verified in a fresh Python 3.11 environment, and every notebook
and figure in this repository was produced in it.

## 7.1 External validation and known limitations

[`EV_External_Validation.ipynb`](EV_External_Validation.ipynb) tests the models on open data from outside the pilot
(downloaded from Zenodo on first run into the git-ignored `Data/external/`, CC-BY-4.0, MD5-verified) and re-checks the
published numbers against stronger baselines; `EV_Charging_Analysis.ipynb` (§9–§11) and `EV_Session_Energy_Model.ipynb` (§4–§6)
now carry the same no-model baselines for their own results. The validation notebook first reproduces the published hold-out
metrics exactly with the shipped model, so the figures below come from a verified pipeline.

| Question | Result |
|---|---|
| Does the **deployed session-energy model transfer** to another vehicle? Renault Zoe data-logger ([Zenodo 7033914](https://zenodo.org/records/7033914)), 62 sessions, 41 with a verified-complete context | **Not demonstrably.** MAE 5.19 kWh vs 4.42 for the distance × 0.18 baseline on all sessions, 3.67 vs 3.98 on the clean subset; both 95 % intervals include zero, and the sign differs between the two subsets (stable within each across extraction settings). A smoke test, not a benchmark: two cars (22 and 37 kWh packs), small sample, mostly short morning top-ups. |
| Where does it break? | Sessions more than 400 h after the previous one (8 of 62): MAE 10.1 vs 4.8 kWh for the baseline. Elsewhere it ties the baseline (4.5 vs 4.4). It has no battery-capacity input. |
| **How much better than a naive predictor is it on the pilot hold-out?** | −44 % MAE against the published baseline (18.7 → 10.5 kWh), but **−30 % against a constant training median** (14.9 kWh), which already beats the published baseline. The gain is real (95 % interval of the gap 2.8–6.0 kWh) but smaller than the headline suggests. |
| Do the **pilot's three heads** beat no-model baselines? (analysis notebook §9–§11) | **Will-charge:** pooled ROC-AUC 0.66, but a household's own charge rate alone gives 0.63 and 89 % of the lowest-probability quintile is one household; *within a household* the model reaches AUC 0.62 against 0.45–0.47 for persistence, recency and the base rate, and the quintile spread is 37 % vs 61 % of days (pooled: 29 % vs 68 %) — real but modest. **Session energy** (walk-forward): MAE 12.5 kWh vs 16.0 for the training median and for the household's trailing median (−22 %). **Dwell:** MAE 3.65 h vs 4.10 (training median) and 4.20 (trailing median), i.e. −11 % / −13 %. **Volume:** see below. |
| Do the **will-charge, session-energy and dwell heads** hold up on 35,377 real Norwegian residential sessions ([Zenodo 13896176](https://zenodo.org/records/13896176))? No driving data there, so refitted on reduced features. | Will-charge: pooled ROC-AUC 0.78, but **within-user 0.64** (a user's average rate alone: 0.72 pooled, 0.50 within-user) — calibrated, lowest quintile 12 % of days vs top 78 %. Session energy: quantile GBR with user history MAE 4.96 kWh vs 5.52 for the user's trailing median, q10–q90 coverage 81 % (nominal 80 %); with only the three deployed features that exist there, MAE 7.52 and coverage 75 %. Dwell: MAE 7.2 h against a median dwell of 11.3 h (pilot: 3.65 h against 9.4 h). |
| Does the **volume head beat a trivial forecast**? | **No.** On Norway a trailing 28-day average matches it (7-day per-user nMAE 43.2 % vs 42.9 %). On the pilot's own walk-forward rows it has lower error at 3, 7 and 14 days per household (7 days: 36.9 vs 45.8 kWh) and at every horizon for the 4-household fleet (7 days: 70.8 vs 96.7 kWh). The fall of nMAE with horizon and portfolio size is an aggregation effect; the analysis notebook originally compared only with the training-set median and now also reports the trailing average (§10.2, Figure 4). |
| **User segmentation** (spec KPI) on 206 Norwegian users | No clear structure: silhouette 0.21–0.22 for every k = 2–6; stability (adjusted Rand index) 0.79 at k = 2, 0.53–0.62 for k ≥ 3. |

**Known limitations**

- **Four households only** (see above): the 44 % figure is against a weak baseline, and nothing transfers demonstrably to other vehicles or usage.
- **No battery-capacity or state-of-charge input**: the session-energy model cannot know the size of the pack it is predicting for.
- **Long gaps** since the last charge are poorly covered by the training data (90th percentile ≈ 100 h) and are where it fails out of domain.
- **Volume head** has no demonstrated skill over a trailing 28-day average; the fall of nMAE with horizon and portfolio size is an aggregation effect that the trailing average shows equally.
- **Segments** are assigned by rule on four households; in the 206-user Norwegian population the same kind of profile features were not well separated.
- **Model file portability**: `Data/models/session_energy.joblib` is a pickle written with scikit-learn 1.5.2; it loads **only** on that release (not 1.6 or newer, so not on Python 3.13 either). The versions are pinned in `requirements.txt` and `Data/models/requirements.txt`, and the model card states the requirement and checks it in its usage snippet.
- **Timing (Head A)**: most of the pooled ranking is *which household* it is; use the within-household figures above for any claim about picking days or users.
- **Open data is a proxy.** No open data set was found that records driving *between* charging sessions at scale, which the deployed model requires; a proper external test needs one (or pilot data from a second site).
