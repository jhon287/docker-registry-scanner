"""Scanner Options"""

from typing import Optional


class ScannerOptions:
    """Scanner Options Class"""

    severities: list[str] = ["UNKNOWN", "LOW", "MEDIUM", "HIGH", "CRITICAL"]

    def __init__(
        self,
        severity: str = "UNKNOWN,LOW,MEDIUM,HIGH,CRITICAL",
        min_severity: Optional[str] = None,
        scanners: str = "vuln,secret",
        processes: int = 4,
    ) -> None:
        self._severity = severity
        self._min_severity = min_severity
        self._scanners = scanners
        self._processes = processes

    @property
    def scanners(self) -> str:
        """Get scanners"""

        return self._scanners

    @property
    def processes(self) -> int:
        """Get processes"""

        return self._processes

    @property
    def severity(self) -> str:
        """Get severity"""

        if self._min_severity is not None:
            severity_index: int = self.severities.index(self._min_severity)
            return ",".join(self.severities[severity_index:])
        return self._severity
