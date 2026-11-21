# BRICAS Day 4 — Executive Audit Dashboard & Final Reporting

## Run on macOS

```bash
cd ~/Documents/Project/bricas_day4
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python executive_day4.py
python -m unittest discover -p 'tests_day*.py' -v
python -m streamlit run dashboard_day4.py --server.port 8504
```

Open http://localhost:8504. The executive report and Power BI-ready CSV exports are saved in `reports/`.

## Deliverables

- Executive KPI dashboard with region and severity filters
- Daily monitoring, severity and regional alert charts
- Prioritized account review and audit evidence downloads
- Markdown executive report, metrics JSON, CSV exports
- Automated test suite and reproducible synthetic dataset

## Power BI

On a Windows machine with Power BI Desktop: Get Data > Text/CSV; import `reports/regional_risk_summary.csv`, `reports/daily_monitoring.csv`, and `reports/account_audit_priorities.csv`. Use `region`, `tx_day`, and `account_id` as dimensions respectively. These are separate aggregate tables, not a relational star schema; avoid joining them directly by unrelated dimensions. Power BI Desktop is not natively supported on macOS.

## Portfolio statement

Independent demonstration built with **synthetic data**. Rules and anomaly scores are not validated fraud predictions, and this work does not establish banking industry experience or regulatory compliance.
