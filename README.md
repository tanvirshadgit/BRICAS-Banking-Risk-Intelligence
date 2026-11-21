# BRICAS Day 1
Banking Risk Intelligence & Continuous Audit System — synthetic portfolio demonstration.

## Setup (macOS / Linux)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
streamlit run dashboard.py
```

## Outputs
- `data/bricas.db` — SQLite relational database
- `data/transactions_export.csv` — transaction risk data for Power BI / Streamlit
- `data/risk_alerts.csv` — rule-based alert candidates
- `data/quality_report.csv` — basic data-quality metrics

## Caveats
All customers and transactions are synthetic. Risk scores are illustrative heuristics, not validated fraud predictions or regulatory AML determinations. No personal or real bank data is used.

## Power BI
Import `data/transactions_export.csv` using **Get Data → Text/CSV**. Suggested cards: transaction count, total BDT amount, flagged alerts. Chart timestamp (day) vs transaction count. Power BI Desktop is not natively available on macOS; use a Windows environment for Desktop or a supported Power BI web workflow.
