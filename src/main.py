"""Main"""

from typing import Any, Literal, Optional
from json import dumps
from docker_registry_client import DockerRegistryClient
from scanner import Scanner, download_database
from scanner_options import ScannerOptions
from logger import logger
import config


def display_results(results: dict[str, Any]) -> None:
    """Display Scanner Results To Standard Output"""

    for image, result in dict(results).items():
        text: str = ""

        if result:
            status: Optional[str] = dict(result).get("status")
            status_emoji: Literal["🟢", "🔴"] = "🟢" if status == "OK" else "🔴"
            text = f"{status_emoji} {status}\t{image}"

            if status != "OK":
                summary: Optional[dict[str, int]] = dict(
                    dict(result).get("vulnerabilities")
                ).get("summary")
                text = f"{text} ({summary})"
        else:
            text = f"🔥 FAILED '{image}'"
        logger.info(text)


def export_scan_results(scan_results: dict[str, Any], output_file: str) -> None:
    """Export Scan Results Function"""

    if scan_results:
        with open(file=output_file, mode="w", encoding="UTF-8") as file:
            file.write(dumps(scan_results, indent=2))
        logger.info(msg=f"✨ Scan results exported on {output_file}")


def main():  # pragma: no cover
    """Main Function"""

    if config.DOCKER_REGISTRY_URL is None:
        raise ValueError(
            "Docker registry needs to be defined using "
            "'DOCKER_REGISTRY_URL' environment variable!"
        )

    total_tags_scanned: int = 0
    scan_results: dict[str, Any] = {}
    client: DockerRegistryClient = DockerRegistryClient(
        registry_url=config.DOCKER_REGISTRY_URL,
        timeout=config.HTTPS_CONNECTION_TIMEOUT,
        ca_file=config.DOCKER_REGISTRY_CA_FILE,
    )
    images: list[str] = client.get_images(
        number_max=config.IMAGE_LIST_NBR_MAX, pattern=config.DOCKER_IMAGES_FILTER
    )
    scanner_options: ScannerOptions = ScannerOptions(
        severity=config.SCAN_SEVERITY,
        scanners=config.SCAN_SCANNERS,
        processes=config.MULTIPROCESSING_PROCESSES,
        min_severity=config.SCAN_MIN_SEVERITY,
    )

    logger.info(msg=f"💡 Number of Docker images: {len(images)}")

    download_database()
    # download_database(database="java")

    for image in images:
        image_tags: list[str] = client.get_image_tags(
            image=image, pattern=config.DOCKER_TAGS_FILTER
        )

        if not image_tags:
            logger.warning(msg=f"🤡 No Docker tags found for '{image}'")
            continue

        logger.info(msg=f"💡 Number of Docker tags for '{image}': {len(image_tags)}")

        scanner: Scanner = Scanner(
            docker_registry=f"{client.registry_host}:{client.registry_port}",
            image_tags=image_tags,
            options=scanner_options,
        )

        try:
            for results in scanner.scan():
                scan_results.update(results)
                display_results(results=results)
            total_tags_scanned += len(image_tags)
            logger.info(msg=f"💡 Total Docker tags scanned: {total_tags_scanned}")
        except RuntimeError as exc:
            logger.critical(exc)
            export_scan_results(
                scan_results=scan_results, output_file=config.SCAN_RESULTS_REPORT_FILE
            )
    export_scan_results(
        scan_results=scan_results, output_file=config.SCAN_RESULTS_REPORT_FILE
    )


if __name__ == "__main__":  # pragma: no cover
    main()
