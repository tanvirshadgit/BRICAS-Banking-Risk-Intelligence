# BRICAS Day 3 — Statistical Anomaly Screening & Audit Evidence

This upgrade is based on the Day 2 project. It **does not modify** `data/bricas.db` and retains Day 1/Day 2 scripts.

## Run on Mac

```bash
cd ~/Documents/Project/bricas_day3
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python anomaly_day3.py
python -m unittest tests_day3.py -v
python -m streamlit run dashboard_day3.py --server.port 8503
```

## Outputs

- `data/day3_audit_evidence.csv` — flagged transaction evidence with reason and severity
- `data/day3_statistical_anomalies.csv` — amount outliers
- `data/day3_severity_summary.csv` — region/severity totals, Power BI import-ready

## Risk methodology

- Day 2 rules: high-value >= BDT 200,000 (+40), pending KYC (+30), frozen account (+50), repeated high-value same account/day (+20).
- Robust modified z-score on log(1 + amount): `0.6745 * (log_amount - median) / MAD`; absolute score > 3.5 yields statistical anomaly (+15).
- Score capped at 100; LOW=0, MEDIUM=1–39, HIGH=40–69, CRITICAL=70–100. Review required at >=40.
- These are **illustrative rules**, not official bank policy, verified fraud labels, AML determinations, or validated model performance.
- A statistical anomaly alone (+15) does not create a review-required alert. This is a deliberate demonstration threshold choice.

## Notes

Streamlit can run natively on macOS. Power BI Desktop requires Windows; import the generated CSV files when available.
