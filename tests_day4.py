import tempfile
import unittest
from pathlib import Path
import pandas as pd
from anomaly_day3 import build_findings
from executive_day4 import summarize, export_reports

class Day4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df=build_findings()
    def test_metrics_consistency(self):
        s=summarize(self.df)
        self.assertEqual(s['transactions'],len(self.df))
        self.assertEqual(s['alerts'],int(self.df.review_status.eq('REVIEW_REQUIRED').sum()))
        self.assertEqual(s['statistical_anomalies'],int(self.df.statistical_anomaly.sum()))
    def test_filtered_metrics(self):
        f=self.df[self.df.region.eq('Chattogram')]
        s=summarize(f)
        self.assertEqual(s['transactions'],len(f))
        self.assertLessEqual(s['alerts'],s['transactions'])
    def test_report_exports(self):
        with tempfile.TemporaryDirectory() as d:
            export_reports(self.df,d)
            for name in ['regional_risk_summary.csv','daily_monitoring.csv','account_audit_priorities.csv','audit_evidence.csv','executive_metrics.json','EXECUTIVE_REPORT.md']:
                self.assertTrue((Path(d)/name).exists())
            evidence=pd.read_csv(Path(d)/'audit_evidence.csv')
            self.assertEqual(len(evidence),int(self.df.review_status.eq('REVIEW_REQUIRED').sum()))
    def test_empty_filter_safe(self):
        s=summarize(self.df.iloc[0:0])
        self.assertEqual(s['alert_rate_pct'],0)

if __name__=='__main__': unittest.main()
