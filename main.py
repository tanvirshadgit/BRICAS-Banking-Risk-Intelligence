import argparse
import csv
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
DATA.mkdir(exist_ok=True)
DB = DATA / 'bricas.db'

SCHEMA = '''
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS customers (
 customer_id INTEGER PRIMARY KEY, segment TEXT NOT NULL, region TEXT NOT NULL,
 kyc_status TEXT NOT NULL CHECK(kyc_status IN ('VERIFIED','PENDING'))
);
CREATE TABLE IF NOT EXISTS accounts (
 account_id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
 account_type TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('ACTIVE','FROZEN'))
);
CREATE TABLE IF NOT EXISTS transactions (
 transaction_id INTEGER PRIMARY KEY, account_id INTEGER NOT NULL REFERENCES accounts(account_id),
 timestamp TEXT NOT NULL, amount_bdt REAL NOT NULL CHECK(amount_bdt > 0),
 direction TEXT NOT NULL CHECK(direction IN ('CREDIT','DEBIT')),
 channel TEXT NOT NULL, counterparty_region TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_tx_account_time ON transactions(account_id,timestamp);
CREATE INDEX IF NOT EXISTS idx_tx_amount ON transactions(amount_bdt);
'''

RISK_SQL = '''
SELECT t.transaction_id, t.timestamp, t.account_id, t.amount_bdt, t.direction,
       c.kyc_status, a.status AS account_status,
       CASE WHEN t.amount_bdt >= 200000 THEN 1 ELSE 0 END AS high_value,
       CASE WHEN c.kyc_status = 'PENDING' THEN 1 ELSE 0 END AS pending_kyc,
       CASE WHEN a.status = 'FROZEN' THEN 1 ELSE 0 END AS frozen_account,
       (CASE WHEN t.amount_bdt >= 200000 THEN 40 ELSE 0 END +
        CASE WHEN c.kyc_status = 'PENDING' THEN 30 ELSE 0 END +
        CASE WHEN a.status = 'FROZEN' THEN 50 ELSE 0 END) AS risk_score
FROM transactions t
JOIN accounts a ON t.account_id = a.account_id
JOIN customers c ON a.customer_id = c.customer_id
'''

def build(seed=42, n=10000):
    rng = random.Random(seed)
    if DB.exists(): DB.unlink()
    with sqlite3.connect(DB) as conn:
        conn.executescript(SCHEMA)
        customers = [(i, rng.choice(['RETAIL','SME']), rng.choice(['Dhaka','Chattogram','Khulna','Rajshahi']),
                      'PENDING' if rng.random()<0.06 else 'VERIFIED') for i in range(1,501)]
        accounts = [(i, i, rng.choice(['SAVINGS','CURRENT']), 'FROZEN' if rng.random()<0.02 else 'ACTIVE') for i in range(1,501)]
        conn.executemany('INSERT INTO customers VALUES (?,?,?,?)', customers)
        conn.executemany('INSERT INTO accounts VALUES (?,?,?,?)', accounts)
        start = datetime(2026, 10, 1)
        transactions = []
        for i in range(1,n+1):
            account = rng.randint(1,500)
            ts = (start + timedelta(seconds=rng.randint(0, 30*86400-1))).isoformat(timespec='seconds')
            amount = round(rng.lognormvariate(9.0, 1.0), 2)
            if rng.random() < 0.025: amount = round(rng.uniform(200000,500000),2)
            transactions.append((i,account,ts,amount,rng.choice(['CREDIT','DEBIT']),
                                 rng.choice(['APP','ATM','BRANCH','WEB']),rng.choice(['BD','BD','BD','OTHER'])))
        conn.executemany('INSERT INTO transactions VALUES (?,?,?,?,?,?,?)',transactions)
    print(f'Created {DB} with {n:,} synthetic transactions (seed={seed})')

def audit():
    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        checks = {
            'customers': conn.execute('SELECT COUNT(*) FROM customers').fetchone()[0],
            'accounts': conn.execute('SELECT COUNT(*) FROM accounts').fetchone()[0],
            'transactions': conn.execute('SELECT COUNT(*) FROM transactions').fetchone()[0],
            'null_required_fields': conn.execute('SELECT COUNT(*) FROM transactions WHERE account_id IS NULL OR timestamp IS NULL OR amount_bdt IS NULL').fetchone()[0],
            'orphan_transactions': conn.execute('SELECT COUNT(*) FROM transactions t LEFT JOIN accounts a ON t.account_id=a.account_id WHERE a.account_id IS NULL').fetchone()[0],
            'duplicate_transaction_ids': conn.execute('SELECT COUNT(*) FROM (SELECT transaction_id FROM transactions GROUP BY transaction_id HAVING COUNT(*)>1)').fetchone()[0],
            'invalid_amounts': conn.execute('SELECT COUNT(*) FROM transactions WHERE amount_bdt<=0').fetchone()[0]
        }
        rows = conn.execute(RISK_SQL + ' ORDER BY t.transaction_id').fetchall()
        risk = [dict(r) for r in rows]
        flagged = [r for r in risk if r['risk_score'] >= 40]
        with (DATA/'risk_alerts.csv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(risk[0].keys()))
            w.writeheader();w.writerows(flagged)
        with (DATA/'transactions_export.csv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(risk[0].keys()))
            w.writeheader();w.writerows(risk)
        with (DATA/'quality_report.csv').open('w',newline='') as f:
            w=csv.writer(f);w.writerow(['metric','value']);w.writerows(checks.items())
        print('DATA QUALITY:',checks)
        print(f'Risk alerts (score >= 40): {len(flagged):,}; exported CSV files to {DATA}')
        assert all(checks[k]==0 for k in ('null_required_fields','orphan_transactions','duplicate_transaction_ids','invalid_amounts'))

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--seed',type=int,default=42)
    p.add_argument('--transactions',type=int,default=10000)
    args=p.parse_args()
    if args.transactions < 1: p.error('--transactions must be >= 1')
    build(args.seed,args.transactions)
    audit()
