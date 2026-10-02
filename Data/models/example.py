"""Run the Service 4 session-energy model on the bundled open sample.

    pip install -r requirements.txt
    python example.py

Loads session_energy.joblib and example_sessions.csv (open Renault Zoe data-logger sessions, CC-BY-4.0, no timestamps), predicts the
q10 / q50 / q90 energy of every session and compares the median with the project's distance baseline. The sample is out of domain
for the model (different car, different charging context): it shows how to load and run the model, not how accurate it is.
"""
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn

REQUIRED_SKLEARN = "1.5.2"       # the pickle only loads on the scikit-learn release that wrote it
if sklearn.__version__ != REQUIRED_SKLEARN:
    sys.exit(f"session_energy.joblib needs scikit-learn {REQUIRED_SKLEARN}, found {sklearn.__version__}: pip install -r requirements.txt")

here = Path(__file__).resolve().parent
bundle = joblib.load(here / "session_energy.joblib")
data = pd.read_csv(here / "example_sessions.csv")

X = data[bundle["features"]].to_numpy(dtype=float)               # the feature order matters
data["q10"], data["q50"], data["q90"] = np.sort([bundle["quantiles"][q].predict(X) for q in ("q10", "q50", "q90")], axis=0)

# the project's no-model baseline: distance x 0.18 kWh/km (+5 % per trip beyond the first), clamped to 1-80 kWh
baseline = np.clip(data.recent_trip_km * 0.18 * (1 + 0.05 * np.maximum(0, data.trips_today - 1)), 1, 80)

print(data[["session", "recent_trip_km", "hour_of_day", "energy_kwh", "q10", "q50", "q90"]].head(8).round(1).to_string(index=False))
print()
for name, mask in (("all sessions", np.ones(len(data), bool)), ("context verified", data.context_verified.to_numpy())):
    d, b = data[mask], baseline[mask]
    print(f"{name:17s} n={len(d):3d} | model MAE {np.mean(np.abs(d.q50 - d.energy_kwh)):.2f} kWh | distance baseline MAE "
          f"{np.mean(np.abs(b - d.energy_kwh)):.2f} | q10-q90 coverage {100 * np.mean((d.q10 <= d.energy_kwh) & (d.energy_kwh <= d.q90)):.0f} %")
