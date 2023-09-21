"""Main Tests"""

from unittest import TestCase
from json import dumps
from typing import Any
from main import export_scan_results, display_results


class MainTests(TestCase):
    """Main Tests Class"""

    def test_display_results(self):
        """Test Display Results Function"""

        results: dict[str, Any] = {
            "fake-docker-registry.example.com/path/to/fake-alpine:123": {
                "status": "OK"
            },
            "fake-docker-registry.example.com/path/to/fake-alpine:456": {
                "status": "NOK",
                "vulnerabilities": {"summary": {"HIGH": 5}},
            },
        }

        results_list: list[str] = [
            "🟢 OK\tfake-docker-registry.example.com/path/to/fake-alpine:123",
            "🔴 NOK\tfake-docker-registry.example.com/path/to/fake-alpine:456"
            " ({'HIGH': 5})",
        ]

        with self.assertLogs(level="INFO") as logging_watcher:
            display_results(results=results)
            for result_list in results_list:
                self.assertIn(
                    member=result_list,
                    container=[
                        ":".join(str(x).split(":")[2:]) for x in logging_watcher.output
                    ],
                )

    def test_export_scan_results(self):
        """Test Export Scan Results Function"""

        my_output_file: str = "/tmp/results.json"
        my_dict: dict[str, str] = {"Hello": "Wolrd"}

        export_scan_results(scan_results=my_dict, output_file=my_output_file)

        with open(file=my_output_file, encoding="UTF-8") as my_file:
            self.assertEqual(
                first="".join(my_file.readlines()), second=dumps(obj=my_dict, indent=2)
            )
