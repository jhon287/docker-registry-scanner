"""ScannerOptionsTests"""

from unittest import TestCase
from scanner_options import ScannerOptions


class ScannerOptionsTests(TestCase):
    """ScannerOptions Test Cases"""

    def test_min_severity(self):
        """Tests min_severity"""

        self.assertEqual(
            first=ScannerOptions(min_severity="UNKNOWN").severity,
            second="UNKNOWN,LOW,MEDIUM,HIGH,CRITICAL",
        )
        self.assertEqual(
            first=ScannerOptions(min_severity="MEDIUM").severity,
            second="MEDIUM,HIGH,CRITICAL",
        )
        self.assertEqual(
            first=ScannerOptions(min_severity="LOW").severity,
            second="LOW,MEDIUM,HIGH,CRITICAL",
        )
        self.assertEqual(
            first=ScannerOptions(min_severity="HIGH").severity, second="HIGH,CRITICAL"
        )
        self.assertEqual(
            first=ScannerOptions(min_severity="CRITICAL").severity, second="CRITICAL"
        )
