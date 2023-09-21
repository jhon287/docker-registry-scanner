"""Scanner"""

from subprocess import run, DEVNULL  # nosemgrep: bandit.B404
from typing import Any, Optional
from multiprocessing import Pool
from json import loads
from logger import logger
from scanner_options import ScannerOptions


def download_database(database: Optional[str] = None):
    """Download Scanner Database Function"""

    db_str: str = "Vulnerability"
    download_db_param: str = "--download-db-only"

    if database is not None and database.lower() == "java":
        db_str = "Java Index"
        download_db_param = "--download-java-db-only"

    logger.info(msg=f"Downloading Trivy {db_str} database...")
    process = run(
        args=["trivy", "image", download_db_param],
        check=False,
        stdout=DEVNULL,
        stderr=DEVNULL,
    )

    if process.returncode != 0:
        raise SystemExit(
            f"Failed to download Trivy {db_str} database"
            f" (exit code: {process.returncode})"
        )


class Scanner:
    """Scanner Class"""

    docker_registry: str
    image_tags: list[str]
    severity: str
    scanners: str
    processes: int

    def __init__(
        self, docker_registry: str, image_tags: list[str], options: ScannerOptions
    ) -> None:
        self.docker_registry = docker_registry
        self.image_tags = image_tags
        self.severity = options.severity
        self.processes = options.processes
        self.scanners = options.scanners

    def __parse_results(
        self, results: list[dict[str, Any]]
    ) -> dict[str, Any]:  # pragma: no cover
        """Trivy JSON file results parser private method"""
        parsed_results: dict[str, list[str]] = {}
        summary: dict[str, int] = {severity: 0 for severity in self.severity.split(",")}

        for result in results:
            vulns: list[str] = []
            result_class: str = result.get("Class")
            result_target: str = result.get("Target")
            if result_class == "secret":
                for vuln in result.get("Secrets"):
                    sev: str = dict(vuln).get("Severity")
                    rule_id: str = dict(vuln).get("RuleID")
                    vulns.append(f"{rule_id} ({sev})")
                    summary.update({sev: summary.get(sev) + 1})
            else:
                if "Vulnerabilities" not in result:
                    continue
                for vuln in result.get("Vulnerabilities"):
                    sev: str = dict(vuln).get("Severity")
                    vuln_id: str = dict(vuln).get("VulnerabilityID")

                    if f"{vuln_id} ({sev})" not in vulns:
                        vulns.append(f"{vuln_id} ({sev})")
                        summary.update({sev: summary.get(sev) + 1})

            parsed_results.update({f"{result_class} ({result_target})": sorted(vulns)})
        parsed_results.update({"summary": summary})

        return parsed_results

    def run_scan(self, image_tag: str) -> dict[str, Any]:
        """Run Scanner Method"""
        status: str = "OK"
        vulnerabilities: list[Any] = []
        docker_image_tag: str = f"{self.docker_registry}/{image_tag}"
        process_args: list[str] = [
            "trivy",
            "image",
            "--ignore-unfixed",
            "--insecure",
            "--format",
            "json",
            "--severity",
            self.severity,
            "--exit-code",
            "111",
            "--scanners",
            self.scanners,
            docker_image_tag,
        ]

        logger.debug(msg=f"💤 Scanning Docker image '{docker_image_tag}'...")
        process = run(args=process_args, capture_output=True, check=False)

        print(process.returncode, process.stdout)

        if process.returncode not in [111, 0]:
            return {docker_image_tag: {}}

        proc_stdout: dict[str, Any] = dict(loads(process.stdout))
        # .Results
        image_results: list[dict[str, Any]] = proc_stdout.get("Results")
        # .Metadata
        image_metadata: dict[str, Any] = proc_stdout.get("Metadata")
        # .Metadata.ImageID
        image_id: str = image_metadata.get("ImageID")
        # .Metadata.ImageConfig
        image_config: dict[str, Any] = image_metadata.get("ImageConfig")
        # .Metadata.ImageConfig.created
        image_created: str = image_config.get("created")
        # .Metadata.ImageConfig.config.Labels
        image_labels: dict[str, str] = dict(image_config.get("config")).get("Labels")

        if process.returncode == 111:
            status = "NOK"
            vulnerabilities = self.__parse_results(results=image_results)

        return {
            docker_image_tag: {
                "status": status,
                "created": image_created,
                "id": image_id,
                "labels": image_labels,
                "vulnerabilities": vulnerabilities,
            }
        }

    def scan(self) -> list[dict[str, dict[str, Any]]]:  # pragma: no cover
        """Scan Method (Multiprocessing)"""
        with Pool(processes=self.processes) as pool:
            return pool.map(func=self.run_scan, iterable=self.image_tags)
