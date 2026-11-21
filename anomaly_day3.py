"""BRICAS Day 3: reproducible, read-only statistical anomaly screening."""
from pathlib import Path
import sqlite3
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
DB = DATA / 'bricas.db'


def build_findings(db=DB):
    if not Path(db).is_file():
        raise FileNotFoundError(f'Missing database: {db}. Run python main.py first.')
    with sqlite3.connect(f'file:{Path(db).resolve()}?mode=ro', uri=True) as conn:
        tx = pd.read_sql_query('''SELECT t.transaction_id, t.timestamp, t.account_id,
           t.amount_bdt, t.direction, a.status AS account_status,
           c.kyc_status, c.region FROM transactions t
           JOIN accounts a ON t.account_id=a.account_id
           JOIN customers c ON a.customer_id=c.customer_id''', conn)
    if tx.empty:
        raise ValueError('No transactions found')
    tx['amount_bdt'] = pd.to_numeric(tx['amount_bdt'], errors='raise')
    if tx['transaction_id'].duplicated().any() or tx['amount_bdt'].isna().any() or (tx['amount_bdt'] < 0).any():
        raise ValueError('Invalid transaction identifiers or amounts')
    tx['tx_day'] = pd.to_datetime(tx['timestamp']).dt.strftime('%Y-%m-%d')
    # Global robust modified z-score on log amounts; exploratory screening, not trained fraud model.
    log_amount = np.log1p(tx['amount_bdt'].to_numpy(dtype=float))
    median = np.median(log_amount)
    mad = np.median(np.abs(log_amount - median))
    tx['robust_z'] = np.round(0.6745 * (log_amount-median) / mad, 3) if mad > 1e-12 else 0.0
    tx['statistical_anomaly'] = (np.abs(tx['robust_z']) > 3.5).astype(int)
    tx['high_value'] = (tx['amount_bdt'] >= 200000).astype(int)
    tx['pending_kyc'] = (tx['kyc_status'] == 'PENDING').astype(int)
    tx['frozen_account'] = (tx['account_status'] == 'FROZEN').astype(int)
    daily = tx.groupby(['account_id','tx_day'])['high_value'].transform('sum')
    tx['repeat_high_value'] = ((tx['high_value'] == 1) & (daily >= 2)).astype(int)
    tx['rule_score'] = (40*tx['high_value'] + 30*tx['pending_kyc'] + 50*tx['frozen_account'] + 20*tx['repeat_high_value'])
    tx['risk_score'] = (tx['rule_score'] + 15*tx['statistical_anomaly']).clip(upper=100)
    tx['severity'] = pd.cut(tx['risk_score'], bins=[-1,0,39,69,100], labels=['LOW','MEDIUM','HIGH','CRITICAL']).astype(str)
    # Scores 1..39 are MEDIUM, 40..69 HIGH, >=70 CRITICAL; zero LOW.
    reasons = [('high_value','High-value transaction (>= BDT 200,000)'),
               ('pending_kyc','Pending KYC'),('frozen_account','Frozen account activity'),
               ('repeat_high_value','Repeated high-value transactions on same day'),
               ('statistical_anomaly','Unusual transaction amount (robust z-score)')]
    tx['risk_reasons'] = tx.apply(lambda row: '; '.join(label for col,label in reasons if row[col]) or 'No indicator triggered', axis=1)
    tx['review_status'] = np.where(tx['risk_score'] >= 40, 'REVIEW_REQUIRED', 'NOT_FLAGGED')
    return tx.sort_values('transaction_id').reset_index(drop=True)


def export_findings(df, folder=DATA):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    evidence = df.loc[df['review_status'] == 'REVIEW_REQUIRED'].copy()
    evidence.to_csv(folder/'day3_audit_evidence.csv', index=False)
    df.groupby(['severity','region'], observed=True).agg(
        transactions=('transaction_id','size'), total_amount_bdt=('amount_bdt','sum'),
        alerts=('review_status', lambda x: int((x == 'REVIEW_REQUIRED').sum()))
    ).reset_index().to_csv(folder/'day3_severity_summary.csv', index=False)
    df.loc[df['statistical_anomaly'] == 1].to_csv(folder/'day3_statistical_anomalies.csv', index=False)
    return len(evidence)


def main():
    df = build_findings()
    alerts = export_findings(df)
    print(f'PASS: analyzed {len(df):,} synthetic transactions without modifying database')
    print(f'Generated {alerts:,} review-required evidence rows; statistical anomalies: {df.statistical_anomaly.sum():,}')
    print('Not confirmed fraud, regulatory violations, or validated predictive model outputs.')

if __name__ == '__main__':
    main()
