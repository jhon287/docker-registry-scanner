"""Scanner Tests"""

from unittest import TestCase
from unittest.mock import patch, MagicMock
from typing import Any
from dataclasses import dataclass
from scanner import Scanner, download_database
from scanner_options import ScannerOptions


@dataclass
class FakeCompletedProcess:
    """FakeCompletedProcess Class"""

    stdout: bytes = b""
    returncode: int = 0


class ScannerTests(TestCase):
    """Scanner Tests Class"""

    my_docker_registry: str = "docker-registry.example.com:12345"
    my_image_tags: list[str] = ["alpine:3.7"]
    my_severity: str = "HIGH,CRITICAL"
    my_scanners: str = "vuln,secret"
    my_scanner_options: ScannerOptions = ScannerOptions(
        severity=my_severity, scanners=my_scanners, processes=2
    )
    my_scanner: Scanner = Scanner(
        docker_registry=my_docker_registry,
        image_tags=my_image_tags,
        options=my_scanner_options,
    )
    with open(
        file="./tests/fixtures/trivy_scan_result.json",
        encoding="UTF-8",
    ) as my_file:
        run_scan_stdout: bytes = "".join(my_file.readlines())
    run_scan_return: dict[str, Any] = {
        f"{my_docker_registry}/{my_image_tags[0]}": {
            "status": "NOK",
            "created": "2019-03-07T22:19:53.447205048Z",
            "id": (
                "sha256:"
                "6d1ef012b5674ad8a127ecfa9b5e6f5178d171b90ee462846974177fd9bdd39f"
            ),
            "labels": None,
            "vulnerabilities": {
                f"os-pkgs ({my_docker_registry}/{my_image_tags[0]}"
                " (alpine 3.7.3))": [
                    "CVE-2019-14697 (CRITICAL)",
                ],
                "summary": {"HIGH": 0, "CRITICAL": 1},
            },
        }
    }

    def test_init(self):
        """Test Scanner Initialization"""

        self.assertEqual(
            first=self.my_scanner.docker_registry, second=self.my_docker_registry
        )
        self.assertEqual(first=self.my_scanner.image_tags, second=self.my_image_tags)
        self.assertEqual(first=self.my_scanner.severity, second=self.my_severity)
        self.assertEqual(first=self.my_scanner.scanners, second=self.my_scanners)

    @patch(
        target="scanner.run",
        new=MagicMock(
            return_value=FakeCompletedProcess(stdout=run_scan_stdout, returncode=111)
        ),
    )
    def test_run_scan(self):
        """Test Run Scan Method"""
        self.assertEqual(
            first=self.my_scanner.run_scan(image_tag="alpine:3.7"),
            second=self.run_scan_return,
        )

    @patch(target="scanner.run", new=MagicMock(return_value=FakeCompletedProcess()))
    def test_download_database(self):
        """Test Download Database"""

        download_database()
        download_database(database="java")

    @patch(
        target="scanner.run",
        new=MagicMock(return_value=FakeCompletedProcess(returncode=1)),
    )
    def test_download_database_raises(self):
        """Test Download Database"""

        with self.assertRaises(expected_exception=SystemExit):
            download_database()
