# BRICAS — Banking Risk Intelligence & Continuous Audit System

**Independent Python, SQL, and Streamlit portfolio project** for exploratory banking transaction monitoring, illustrative risk screening, statistical anomaly detection, and audit-oriented reporting.

> **Data and interpretation:** All accounts and transactions are synthetic. Alerts are review candidates, not proven fraud, AML violations, or regulatory findings. This project is not a production banking control or evidence of professional banking-sector experience.

## At a glance

| Metric | Result |
|---|---:|
| Synthetic transactions | 10,000 |
| Simulated accounts | 500 |
| Total transaction amount | BDT 211,126,086.31 |
| Review-required alerts | 420 |
| Alert rate | 4.20% |
| Statistical anomalies | 167 |
| High-severity alerts | 392 |
| Critical-severity alerts | 28 |
| Automated tests | 11 passed (local run) |

These are results from the project's synthetic demonstration dataset, not performance metrics on real banking data.

## What it does

- Generates a reproducible synthetic banking dataset and stores transaction data in SQLite.
- Runs SQL analytics and rule-based early-warning screening for risk indicators such as high-value activity, pending KYC, and frozen-account activity.
- Adds statistical anomaly indicators and classifies risk severity for investigation prioritization.
- Presents interactive Streamlit dashboards with region and severity filters, trend charts, and audit-oriented tables.
- Exports executive metrics, regional summaries, account review priorities, and transaction-level audit evidence for further analysis.

## System workflow

```text
Synthetic data generation (main.py)
             |
             v
       SQLite / CSV data
             |
             v
   SQL analytics + EWS (ews.py)
             |
             v
Statistical anomaly screening (anomaly_day3.py)
             |
             v
Executive reporting (executive_day4.py)
             |
       +-----+------+
       |            |
       v            v
 Streamlit       CSV / JSON /
 dashboard       Markdown reports
```

## Technology

Python · SQLite / SQL · Streamlit · CSV / JSON / Markdown reporting · Python `unittest`

**Power BI status:** CSV exports are available for Power BI import; a completed `.pbix` dashboard is **not** included.

## Repository guide

| Path | Purpose |
|---|---|
| `main.py` | Synthetic data generation and initial processing |
| `ews.py` | Early warning / rule-based risk analytics |
| `anomaly_day3.py` | Statistical anomaly detection and evidence preparation |
| `executive_day4.py` | Executive metrics and report generation |
| `dashboard_day4.py` | Latest executive Streamlit dashboard |
| `dashboard.py`, `dashboard_day2.py`, `dashboard_day3.py` | Earlier dashboard iterations |
| `sql/` | SQL analytics |
| `reports/` | Generated management and audit-oriented outputs |
| `tests_day2.py`, `tests_day3.py`, `tests_day4.py` | Automated tests |
| `DAY2_README.md`, `DAY3_README.md`, `DAY4_README.md` | Development-stage documentation |

## Run locally (macOS / Linux)

```bash
git clone https://github.com/tanvirshadgit/BRICAS-Banking-Risk-Intelligence.git
cd BRICAS-Banking-Risk-Intelligence
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
python ews.py
python anomaly_day3.py
python executive_day4.py
python -m unittest discover -p 'tests_day*.py' -v
python -m streamlit run dashboard_day4.py --server.port 8504
```

Open **http://localhost:8504** in your browser. If rerunning the data-generation pipeline, metrics can depend on the version and generated dataset; check the resulting reports rather than assuming the figures above will always match.

## Executive reporting outputs

The reporting workflow produces files in `reports/`, including:

- `EXECUTIVE_REPORT.md`
- `executive_metrics.json`
- `regional_risk_summary.csv`
- `daily_monitoring.csv`
- `account_audit_priorities.csv`
- `audit_evidence.csv`

## Dashboard screenshots

Add verified screenshots under `docs/screenshots/` and then link them here. Suggested captures: executive KPIs, severity and regional risk charts, and audit evidence tables. Avoid publishing screenshots that contain private information.

## Testing and limitations

A local run of the project's automated test suite completed **11 tests successfully**. This confirms the checks implemented in that suite, not exhaustive security, regulatory, or statistical validation.

The rules, thresholds, severity labels, and statistical anomalies are illustrative. No precision, recall, false-positive rate, production scalability, or live-bank integration has been established. Human investigation is required before interpreting any alert as suspicious conduct.

## Author

**Tanvir Ahmed Khan** — independent portfolio project in data analytics, quality assurance, and risk monitoring.

[GitHub profile](https://github.com/tanvirshadgit)
