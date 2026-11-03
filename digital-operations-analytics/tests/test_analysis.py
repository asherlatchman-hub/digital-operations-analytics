"""Quick checks: run `python -m unittest discover -s tests`."""
import unittest
import pandas as pd
from analysis import load_data, filter_dates, filter_incidents, weighted_error_rate, service_summary

class AnalyticsTests(unittest.TestCase):
    def test_data_loads(self):
        daily, incidents = load_data()
        self.assertEqual(len(daily), 120)
        self.assertEqual(len(daily["service"].unique()), 8)
        self.assertFalse(incidents.empty)

    def test_payroll_records_from_export(self):
        _, incidents = load_data()
        rows = incidents.loc[incidents["service"] == "Payroll & HR Portal"]
        self.assertEqual(len(rows), 3)
        self.assertEqual(int(rows["affected_users"].sum()), 12801)

    def test_weighted_average(self):
        frame = pd.DataFrame({"requests": [100, 300], "error_rate_pct": [10, 0]})
        self.assertAlmostEqual(weighted_error_rate(frame), 2.5)

    def test_service_filter(self):
        _, incidents = load_data()
        payroll = filter_incidents(incidents, service="Payroll & HR Portal", priorities=["P2"])
        self.assertEqual(len(payroll), 3)
        self.assertTrue((payroll["service"] == "Payroll & HR Portal").all())
        self.assertEqual(int(payroll["affected_users"].sum()), 12801)

    def test_date_filter_and_summary(self):
        daily, incidents = load_data()
        d, i = filter_dates(daily, incidents, "2026-11-03", "2026-11-03")
        self.assertEqual(len(d), 8)
        self.assertEqual(len(service_summary(d)), 8)
        self.assertGreater(len(i), 0)

if __name__ == "__main__":
    unittest.main()
