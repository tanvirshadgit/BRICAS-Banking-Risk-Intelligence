import sqlite3
import tempfile
import unittest
from pathlib import Path
from anomaly_day3 import DB, build_findings, export_findings

class Day3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = build_findings()
    def test_database_unchanged_and_unique(self):
        with sqlite3.connect(DB) as c:
            self.assertEqual(c.execute('SELECT COUNT(*) FROM transactions').fetchone()[0], len(self.df))
        self.assertTrue(self.df.transaction_id.is_unique)
    def test_risk_scoring_and_evidence(self):
        df=self.df
        self.assertTrue(df.risk_score.between(0,100).all())
        self.assertTrue((df.loc[df.review_status=='REVIEW_REQUIRED','risk_score'] >= 40).all())
        self.assertTrue((df.loc[df.review_status=='NOT_FLAGGED','risk_score'] < 40).all())
        self.assertTrue(df.loc[df.frozen_account==1,'risk_reasons'].str.contains('Frozen account').all())
    def test_exports(self):
        with tempfile.TemporaryDirectory() as d:
            count=export_findings(self.df,d)
            self.assertEqual(count,int((self.df.review_status=='REVIEW_REQUIRED').sum()))
            for name in ('day3_audit_evidence.csv','day3_severity_summary.csv','day3_statistical_anomalies.csv'):
                self.assertTrue((Path(d)/name).exists())
    def test_severity_thresholds(self):
        df=self.df
        self.assertTrue((df.loc[df.risk_score==0,'severity']=='LOW').all())
        self.assertTrue((df.loc[df.risk_score>=70,'severity']=='CRITICAL').all())

if __name__=='__main__':
    unittest.main()
