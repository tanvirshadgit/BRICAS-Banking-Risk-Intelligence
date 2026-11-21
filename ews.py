"""BRICAS Day 2: read-only early warning and audit exports.
Run after main.py; does not regenerate or mutate the Day 1 database.
"""
from pathlib import Path
import csv
import sqlite3

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DB = DATA / "bricas.db"

EWS_SQL = """
WITH tx AS (
 SELECT t.transaction_id, t.account_id, t.timestamp, t.amount_bdt,
        substr(t.timestamp,1,10) AS tx_day,
        a.status AS account_status, c.kyc_status,
        SUM(CASE WHEN t.amount_bdt >= 200000 THEN 1 ELSE 0 END)
          OVER (PARTITION BY t.account_id, substr(t.timestamp,1,10)) AS daily_high_value_count
 FROM transactions t
 JOIN accounts a ON a.account_id=t.account_id
 JOIN customers c ON c.customer_id=a.customer_id
), scored AS (
 SELECT *,
   CASE WHEN amount_bdt >= 200000 THEN 40 ELSE 0 END
 + CASE WHEN kyc_status = 'PENDING' THEN 30 ELSE 0 END
 + CASE WHEN account_status = 'FROZEN' THEN 50 ELSE 0 END
 + CASE WHEN amount_bdt >= 200000 AND daily_high_value_count >= 2 THEN 20 ELSE 0 END
 AS risk_score,
   CASE WHEN amount_bdt >= 200000 THEN 1 ELSE 0 END AS high_value,
   CASE WHEN kyc_status = 'PENDING' THEN 1 ELSE 0 END AS pending_kyc,
   CASE WHEN account_status = 'FROZEN' THEN 1 ELSE 0 END AS frozen_account,
   CASE WHEN amount_bdt >= 200000 AND daily_high_value_count >= 2 THEN 1 ELSE 0 END AS repeat_high_value
 FROM tx
)
SELECT * FROM scored WHERE risk_score >= 40 ORDER BY risk_score DESC, transaction_id
"""

DAILY_SQL = """
SELECT substr(timestamp,1,10) AS day, COUNT(*) AS transaction_count,
       ROUND(SUM(amount_bdt),2) AS total_bdt,
       SUM(CASE WHEN amount_bdt>=200000 THEN 1 ELSE 0 END) AS high_value_count
FROM transactions GROUP BY substr(timestamp,1,10) ORDER BY day
"""

ACCOUNT_SQL = """
SELECT a.account_id, c.region, c.kyc_status, a.status AS account_status,
       COUNT(*) AS transaction_count, ROUND(SUM(t.amount_bdt),2) AS total_bdt
FROM transactions t JOIN accounts a ON a.account_id=t.account_id
JOIN customers c ON c.customer_id=a.customer_id
GROUP BY a.account_id ORDER BY total_bdt DESC
"""

def export_query(conn, sql, filename):
    cursor = conn.execute(sql)
    headers = [x[0] for x in cursor.description]
    rows = cursor.fetchall()
    with (DATA / filename).open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    return len(rows)

def main():
    if not DB.is_file():
        raise SystemExit('Database missing. Run python main.py first.')
    with sqlite3.connect(f'file:{DB}?mode=ro', uri=True) as conn:
        required = {'customers','accounts','transactions'}
        found = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if not required <= found:
            raise SystemExit(f'Missing tables: {required-found}')
        n = conn.execute('SELECT COUNT(*) FROM transactions').fetchone()[0]
        a = export_query(conn, EWS_SQL, 'ews_alerts.csv')
        d = export_query(conn, DAILY_SQL, 'daily_audit_summary.csv')
        ac = export_query(conn, ACCOUNT_SQL, 'account_risk_summary.csv')
    print(f'PASS: {n:,} original transactions unchanged')
    print(f'Exported {a:,} EWS alerts, {d} daily summaries, {ac} account summaries')
    print('Note: EWS risk indicators are synthetic, not confirmed fraud or regulatory findings.')

if __name__ == '__main__':
    main()
