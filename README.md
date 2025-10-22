sort.py

This module provides several implementations to sort a list of dictionaries by a specified key.

Files
- sort.py: Contains AI-suggested and optimized implementations plus examples and a short analysis.

Implemented functions
- sort_dicts_by_key_ai(lst, key, reverse=False)
  - Minimal AI-style implementation. Returns a new list sorted by `dict[key]`. May raise KeyError if a dict misses the key.

- sort_dicts_by_key_inplace_fast(lst, key, reverse=False)
  - In-place sort using `operator.itemgetter`. Fastest when all dicts contain the key and mutation is acceptable.

- sort_dicts_by_key_inplace_safe(lst, key, reverse=False, missing_value=None)
  - In-place sort that uses `dict.get` to supply a default for missing keys; safer but slightly slower.

- sort_dicts_by_key_dsu(lst, key, reverse=False, missing_value=None)
  - Decorate-sort-undecorate: computes keys once then sorts decorated pairs. Useful when key extraction is expensive; uses O(n) extra memory.

Usage examples
# sort.py

This module provides several implementations to sort a list of dictionaries by a specified key.

Files
- `sort.py`: Contains AI-suggested and optimized implementations plus examples and a short analysis.

Implemented functions
- `sort_dicts_by_key_ai(lst, key, reverse=False)`
  - Minimal AI-style implementation. Returns a new list sorted by `dict[key]`. May raise KeyError if a dict misses the key.

- `sort_dicts_by_key_inplace_fast(lst, key, reverse=False)`
  - In-place sort using `operator.itemgetter`. Fastest when all dicts contain the key and mutation is acceptable.

- `sort_dicts_by_key_inplace_safe(lst, key, reverse=False, missing_value=None)`
  - In-place sort that uses `dict.get` to supply a default for missing keys; safer but slightly slower.

- `sort_dicts_by_key_dsu(lst, key, reverse=False, missing_value=None)`
  - Decorate-sort-undecorate: computes keys once then sorts decorated pairs. Useful when key extraction is expensive; uses O(n) extra memory.

Usage examples

Non-mutating (returns a new list):

```python
from sort import sort_dicts_by_key_ai
new_list = sort_dicts_by_key_ai(data, "score")
```

In-place (mutates original):

```python
from sort import sort_dicts_by_key_inplace_fast
sort_dicts_by_key_inplace_fast(data, "score")
```

Performance notes (summary)
- All methods are O(n log n) time complexity. Differences are in constant factors and memory allocations.
- `itemgetter` + in-place `.sort()` is typically the fastest and most memory-efficient.
- Use `sorted(...)` when you need a non-mutating result.
- Use DSU when key extraction is expensive and you can afford O(n) extra memory.

Next steps / suggestions
- Add unit tests covering missing keys, reverse sorting, and stability.
- Add a micro-benchmark script to quantify tradeoffs on your machine.
- Optionally expose a single public API function in `sort.py` that selects the best strategy based on options.

## Web app
- `web.py`: single-file Flask app (embedded HTML/CSS/JS). It provides a login/logout flow and a homepage to view and sort generated sample data by `age`, `grade`, `sex`, `nationality`, and `race`.

## Model & Fairness audit
- `train_priority_model.py`: trains a RandomForest pipeline on the sklearn breast-cancer dataset and synthesizes a 3-class priority label (low/medium/high) based on `mean radius`. The trained pipeline is saved to `model.pkl` as a dict with keys `pipeline` and `label_map`.
- `model.pkl`: trained model artifact (pipeline + label map).
- `fairness_audit.py`: loads `model.pkl`, synthesizes true priority labels for a sampled test set (same rules as training), predicts with the saved pipeline, computes overall and per-team accuracy / F1, and (when AIF360 is installed) computes statistical parity and disparate impact for the `high` priority class. Outputs `fairness_report.json`.
- `fairness_report.json`: produced by the audit; contains overall and per-team metrics (and AIF360 metrics when available).

Notes about the audit
- The audit synthesizes a `team` attribute (team_A/team_B/team_C) for demonstration. Because the dataset is synthetic for this demo (priority labels are derived from a feature), fairness metrics are illustrative; for production use you should run audits on labeled holdout data that include real sensitive attributes.

## How to run the web app

1. Create and activate a Python virtual environment (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Run the app:

```powershell
python web.py
```

4. Open http://127.0.0.1:5000/ in your browser. Demo users: `alice/password123`, `bob/hunter2`.

## How to train and run the fairness audit

1. Train the model (creates `model.pkl`):

```powershell
python train_priority_model.py
```

2. Run the fairness audit (writes `fairness_report.json`):

```powershell
python fairness_audit.py
```

If AIF360 is not installed the script will still write per-team metrics; installing AIF360 in the venv enables parity metrics.

Notes
- The web app uses a file-based hashed user store (`users.json`) and secure password hashing via werkzeug; still only for demo use — do not use this as-is in production.
- TLS / pip notes: If you saw pip/TLS CA errors during setup, they were caused by a user-level environment variable pointing at an invalid CA path. During development the quick remediation was to unset the `REQUESTS_CA_BUNDLE` and `CURL_CA_BUNDLE` env vars (PowerShell example below). To permanently remove a user env var use the System Environment control panel.

```powershell
Remove-Item Env:\REQUESTS_CA_BUNDLE -ErrorAction SilentlyContinue
Remove-Item Env:\CURL_CA_BUNDLE -ErrorAction SilentlyContinue
```

## Artifacts in this repo
- `model.pkl` - trained model pipeline created by `train_priority_model.py`.
- `fairness_report.json` - last run audit results.
- `web_app_test_summary.pdf` - short PDF summary created earlier.
- `users.json` - demo user store with hashed passwords for sample users.

Contact
If you want changes, tests, a Dockerfile, or CI wiring for the audit, tell me which to add next.

## Short fairness audit summary

Latest audit (see `fairness_report.json`) on a sampled test set shows very high overall accuracy (~0.995) and near-perfect per-team results for `team_B` and `team_C` (these are small groups in the sample). Manual parity metrics included in the report show group positive rates (P(Y_hat=high)) roughly: team_A ~0.358, team_B 0.25, team_C 0.333. The statistical parity difference (team_C - team_A) is about -0.025 and disparate impact ~0.93.

Interpretation & next steps
- The model performs very well on the synthetic labels used here; however this dataset and the `team` attribute are synthetic for demo purposes. Treat these numbers as illustrative only.
- Recommended actions:
  - Run the audit on a labeled holdout containing real sensitive attributes to get actionable fairness metrics.
  - Log predictions and group membership in production or integration tests to monitor drift over time.
  - If you need automated mitigation, try simple reweighing or class rebalancing, then re-evaluate parity and utility trade-offs.
  - Add the audit to CI so it runs when the model or data transforms change.

If you'd like, I can create a short PDF summarizing these audit results, add CI steps to run the audit automatically, or implement a prediction endpoint in `web.py` that records inputs/predictions for monitoring.