# BRICAS Day 2 — Advanced SQL and EWS

Uses **synthetic data only**. Rule-based risk indicators are **not** fraud determinations or verified regulatory controls.

## Commands (from project directory)

```bash
source .venv/bin/activate
python ews.py
python -m unittest tests_day2.py -v
python -m streamlit run dashboard_day2.py --server.port 8502
```

If the database is missing, run `python main.py` first. Do **not** rerun `main.py` if you want to preserve the existing Day 1 database: it recreates it.

## Power BI
Import `data/ews_alerts.csv`, `data/daily_audit_summary.csv`, and `data/account_risk_summary.csv` using **Get Data → Text/CSV** on Power BI Desktop (Windows). The CSVs can also be opened in Excel on macOS.

## SQL
`sql/advanced_analytics.sql` includes daily activity, account ranking, and repeat high-value patterns. SQL queries use SQLite syntax.

## Limitations
Frozen account status is a snapshot, not a historical status at transaction time. KYC status is also a snapshot. Repeated high-value transactions are illustrative and may be legitimate. No real bank data or Bangladesh Bank rule thresholds are used.
