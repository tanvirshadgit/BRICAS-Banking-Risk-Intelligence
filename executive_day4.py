"""Executive summaries and deterministic report generation for synthetic audit data."""
from pathlib import Path
import json
import pandas as pd
from anomaly_day3 import build_findings

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
REPORTS = ROOT / 'reports'


def summarize(df):
    alerts = df[df.review_status.eq('REVIEW_REQUIRED')]
    return {
        'transactions': int(len(df)),
        'accounts': int(df.account_id.nunique()),
        'amount_bdt': round(float(df.amount_bdt.sum()), 2),
        'alerts': int(len(alerts)),
        'alert_rate_pct': round(100 * len(alerts) / len(df), 2) if len(df) else 0,
        'statistical_anomalies': int(df.statistical_anomaly.sum()),
        'critical_alerts': int(((df.severity == 'CRITICAL') & df.review_status.eq('REVIEW_REQUIRED')).sum()),
        'high_alerts': int(((df.severity == 'HIGH') & df.review_status.eq('REVIEW_REQUIRED')).sum()),
    }


def export_reports(df, folder=REPORTS):
    folder=Path(folder); folder.mkdir(parents=True,exist_ok=True)
    summary=summarize(df)
    by_region=df.groupby('region').agg(transactions=('transaction_id','size'),total_amount_bdt=('amount_bdt','sum'),alerts=('review_status',lambda s:int(s.eq('REVIEW_REQUIRED').sum())),anomalies=('statistical_anomaly','sum')).reset_index()
    by_region['alert_rate_pct']=(100*by_region.alerts/by_region.transactions).round(2)
    by_region.to_csv(folder/'regional_risk_summary.csv',index=False)
    by_day=df.groupby('tx_day').agg(transactions=('transaction_id','size'),alerts=('review_status',lambda s:int(s.eq('REVIEW_REQUIRED').sum())),total_amount_bdt=('amount_bdt','sum')).reset_index()
    by_day.to_csv(folder/'daily_monitoring.csv',index=False)
    by_account=df.groupby('account_id').agg(transactions=('transaction_id','size'),alerts=('review_status',lambda s:int(s.eq('REVIEW_REQUIRED').sum())),maximum_risk_score=('risk_score','max'),total_amount_bdt=('amount_bdt','sum')).reset_index().sort_values(['alerts','maximum_risk_score'],ascending=False)
    by_account.to_csv(folder/'account_audit_priorities.csv',index=False)
    evidence=df.loc[df.review_status.eq('REVIEW_REQUIRED'),['transaction_id','timestamp','account_id','region','amount_bdt','risk_score','severity','risk_reasons','review_status']].copy()
    evidence.to_csv(folder/'audit_evidence.csv',index=False)
    (folder/'executive_metrics.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    report=f"""# BRICAS — Executive Risk Monitoring Report

**Scope:** Synthetic banking transactions; educational demonstration only.  
**Method:** Illustrative rule-based indicators and log-amount robust Z-score; no labeled fraud validation.

## Executive summary

- Transactions reviewed: **{summary['transactions']:,}** across **{summary['accounts']:,}** accounts.
- Total simulated transaction amount: **BDT {summary['amount_bdt']:,.2f}**.
- Review-required alerts: **{summary['alerts']:,}** (**{summary['alert_rate_pct']:.2f}%** of transactions).
- Statistical amount anomalies: **{summary['statistical_anomalies']:,}**; may overlap with rule alerts.
- High-severity review alerts: **{summary['high_alerts']:,}**; critical-severity review alerts: **{summary['critical_alerts']:,}**.

## Risk observations

1. Alerts reflect synthetic rule thresholds for high amounts, pending KYC and frozen-account activity, plus exploratory statistical outliers.
2. An alert is an investigation lead, **not** evidence of fraud, an AML breach, or regulatory non-compliance.
3. No ground-truth fraud labels, calibrated thresholds, real banking systems or operational audit conclusions are available.

## Recommended follow-up actions (demonstration)

1. Review evidence rows and verify account status and KYC attributes against authorized source records.
2. Investigate high- and critical-severity alerts first, with documented analyst disposition.
3. Assess false positives using labeled review outcomes before operational deployment.
4. Validate data lineage, access controls, audit logging and applicable regulatory rules separately.

## Exported evidence

`audit_evidence.csv`, `regional_risk_summary.csv`, `daily_monitoring.csv`, `account_audit_priorities.csv`, `executive_metrics.json`.

*This report does not certify compliance with Bangladesh Bank requirements or any other regulation.*
"""
    (folder/'EXECUTIVE_REPORT.md').write_text(report,encoding='utf-8')
    return summary

if __name__=='__main__':
    result=export_reports(build_findings())
    print('PASS: Day 4 executive exports generated from read-only synthetic data')
    print(json.dumps(result,indent=2))
