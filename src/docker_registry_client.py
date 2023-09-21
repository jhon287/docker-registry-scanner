"""Docker Registry Client"""

from http.client import HTTPSConnection, HTTPResponse, HTTPException
from urllib.parse import urlparse, ParseResult
from json import loads
from re import search
from ssl import SSLContext, PROTOCOL_TLS_CLIENT, CERT_REQUIRED
from typing import Optional
from logger import logger


class DockerRegistryClient:
    """DockerRegistryClient Class"""

    def __init__(
        self,
        registry_url: str,
        ca_file: Optional[str] = None,
        timeout: int = 3,
    ) -> None:
        if not registry_url.startswith("https://"):
            raise ValueError("Docker registry URL must start with 'https://'")

        parse_result: ParseResult = urlparse(url=registry_url)

        self.registry_host: str = str(parse_result.hostname)
        self.registry_port: int = parse_result.port if parse_result.port else 443
        self.registry_path = parse_result.path

        ssl_context: SSLContext = SSLContext(
            protocol=PROTOCOL_TLS_CLIENT, verify_mode=CERT_REQUIRED
        )
        if ca_file:
            ssl_context.load_verify_locations(cafile=ca_file)
        else:
            ssl_context.load_default_certs()
        self.https_connection = HTTPSConnection(  # nosemgrep: bandit.B309
            host=self.registry_host,
            port=self.registry_port,
            timeout=timeout,
            context=ssl_context,
        )

    def __request(self, url: str, method: str = "GET") -> bytes:
        self.https_connection.request(method=method, url=url)
        response: HTTPResponse = self.https_connection.getresponse()
        if response.status != 200:
            location_header: Optional[str] = response.getheader(name="location")
            if location_header:
                logger.info(
                    msg=f"💡 URL redirection detected: {url} -> {location_header}"
                )
                _ = response.read()
                return self.__request(url=location_header)
            raise HTTPException(
                f"Received HTTP code != 200: {response.status} -> {response.reason}"
            )
        return loads(response.read())

    def get_images(self, number_max: int = 500, pattern: str = r".*") -> list[str]:
        """DockerClient Get Images Method"""

        images: list[str] = dict(
            self.__request(url=f"{self.registry_path}/v2/_catalog?n={number_max}")
        ).get("repositories")

        return [image for image in images if search(pattern=pattern, string=image)]

    def get_image_tags(self, image: str, pattern: str = r".*") -> list[str]:
        """DockerClient Get Image Tags Method"""

        tags: list[str] = dict(
            self.__request(url=f"{self.registry_path}/v2/{image}/tags/list")
        ).get("tags")
        if not tags:
            return []
        return [f"{image}:{tag}" for tag in tags if search(pattern=pattern, string=tag)]
