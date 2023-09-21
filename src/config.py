"""Configuration"""

from typing import Final, Optional
from os import getenv

LOGGING_LEVEL: Final[str] = getenv(key="LOGGING_LEVEL", default="INFO")
DOCKER_REGISTRY_URL: Final[Optional[str]] = getenv(key="DOCKER_REGISTRY_URL")
DOCKER_REGISTRY_CA_FILE: Final[Optional[str]] = getenv(key="DOCKER_REGISTRY_CA_FILE")
DOCKER_IMAGES_FILTER: Final[str] = getenv(key="DOCKER_IMAGES_FILTER", default=r".*")
DOCKER_TAGS_FILTER: Final[str] = getenv(key="DOCKER_TAGS_FILTER", default=r".*")
IMAGE_LIST_NBR_MAX: Final[int] = int(getenv(key="IMAGE_LIST_NBR_MAX", default="1000"))
HTTPS_CONNECTION_TIMEOUT: Final[int] = int(
    getenv(key="HTTP_CONNECTION_TIMEOUT", default="3")
)
SCAN_SEVERITY: Final[str] = getenv(key="SCAN_SEVERITY", default="HIGH,CRITICAL")
SCAN_MIN_SEVERITY: Final[Optional[str]] = getenv(key="SCAN_MIN_SEVERITY")
SCAN_RESULTS_REPORT_FILE: Final[str] = getenv(
    key="SCAN_RESULTS_REPORT_FILE", default="./scan_results_report.json"
)
SCAN_SCANNERS: Final[str] = getenv(key="SCAN_SCANNERS", default="vuln,secret")
MULTIPROCESSING_PROCESSES: Final[int] = int(
    getenv(key="MULTIPROCESSING_PROCESSES", default="5")
)
