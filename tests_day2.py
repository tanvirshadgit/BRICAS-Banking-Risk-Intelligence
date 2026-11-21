import csv
import sqlite3
import unittest
from pathlib import Path
from ews import DB, DATA, EWS_SQL

class AuditTests(unittest.TestCase):
    def test_database_integrity(self):
        with sqlite3.connect(DB) as c:
            self.assertEqual(c.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
            self.assertEqual(c.execute('PRAGMA foreign_key_check').fetchall(), [])
    def test_alert_rules(self):
        with sqlite3.connect(DB) as c:
            rows = c.execute(EWS_SQL).fetchall()
            self.assertTrue(all(r[8] >= 40 for r in rows))
            self.assertEqual(len(rows), len({r[0] for r in rows}))
    def test_exports(self):
        for name in ('ews_alerts.csv','daily_audit_summary.csv','account_risk_summary.csv'):
            with self.subTest(name=name):
                with (DATA/name).open(newline='') as f:
                    self.assertGreater(len(list(csv.DictReader(f))),0)

if __name__=='__main__': unittest.main()
