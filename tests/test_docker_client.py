"""Docker Client Tests"""

from unittest import TestCase
from unittest.mock import patch, MagicMock
from typing import Any, Optional
from json import dumps
from http.client import HTTPException
from docker_registry_client import DockerRegistryClient


class FakeHTTPSConnection:
    """FakeHTTPSConnection Class"""

    def __init__(self, status: int = 200, headers: Optional[dict[str, str]] = None):
        self.status = status
        self.headers = {} if not headers else headers

    def request(self, url: str, **_):
        """FakeHTTPSConnection Request Method"""

        self.url = url  # pylint: disable=attribute-defined-outside-init

    def getresponse(self):
        """FakeHTTPSConnection getresponse Method"""

        return FakeHTTPResponse(url=self.url, status=self.status, headers=self.headers)


class FakeHTTPResponse:  # pylint: disable=too-few-public-methods
    """FakeHTTPResponse Class"""

    def __init__(self, url: str, status: int, headers: dict[str, str]):
        self.status = status
        self.url = url
        self.headers = headers

        if status == 200:
            self.reason = "OK"
        if status == 301:
            if headers.get("location") == "/v2/_catalog":
                self.status = 200
                self.reason = "OK"
            self.reason = "Moved Permenatly"
        if status == 404:
            self.reason = "Not Found"

    def __to_json(self, obj: Any) -> str:
        return dumps(obj=obj)

    def getheader(self, name: str) -> Optional[str]:
        """FakeHTTPResponse Get Header Method"""
        return self.headers.get(name)

    def read(self) -> dict[str, Any]:
        """FakeHTTPResponse Read Method"""

        # Get Docker images
        if "/v2/_catalog" in self.url:
            return self.__to_json(
                obj={"repositories": ["fake-alpine", "fake-ubuntu", "fake-python"]}
            )

        # Get Docker image tags
        if "/tags/list" in self.url:
            tags: list[str] = ["a", "b", "c"]
            _, image_name, *_ = self.url.lstrip("/").split("/")
            print(image_name)
            if image_name == "fake-no-tags":
                tags *= 0
            return self.__to_json(obj={"name": image_name, "tags": tags})

        return self.__to_json(obj={})


class DockerRegistryClientTests(TestCase):
    """Docker Client Tests Class"""

    my_registry_host: str = "docker.registry.example.com"
    my_registry_port: int = 12345
    my_registry_path: str = "/my/awesome/path"
    my_registry_url: str = (
        f"https://{my_registry_host}:{my_registry_port}{my_registry_path}"
    )
    my_ca_file: str = "./tests/certs/example.com.crt"
    my_docker_registry_client: DockerRegistryClient = DockerRegistryClient(
        registry_url=my_registry_url, ca_file=my_ca_file
    )

    def test_init(self):
        """Docker Client Initialization Test"""

        self.assertEqual(
            first=self.my_docker_registry_client.registry_host,
            second=self.my_registry_host,
        )
        self.assertEqual(
            first=self.my_docker_registry_client.registry_port,
            second=self.my_registry_port,
        )
        self.assertEqual(
            first=self.my_docker_registry_client.registry_path,
            second=self.my_registry_path,
        )
        with self.assertRaises(expected_exception=ValueError):
            DockerRegistryClient(
                registry_url="http://insecure.registry.example.com:8080"
            )

    @patch(
        target="docker_registry_client.HTTPSConnection",
        new=MagicMock(return_value=FakeHTTPSConnection()),
    )
    def test_get_images(self):
        """Docker Client Get Images Test"""

        my_fake_docker_registry_client: DockerRegistryClient = DockerRegistryClient(
            registry_url="https://fake.registry.example.com:12345"
        )
        self.assertEqual(
            first=my_fake_docker_registry_client.get_images(),
            second=["fake-alpine", "fake-ubuntu", "fake-python"],
        )

    @patch(
        target="docker_registry_client.HTTPSConnection",
        new=MagicMock(return_value=FakeHTTPSConnection()),
    )
    def test_get_image_tags(self):
        """Docker Client Get Image Tags Test"""

        my_fake_docker_registry_client: DockerRegistryClient = DockerRegistryClient(
            registry_url="https://fake.registry.example.com:12345"
        )
        self.assertEqual(
            first=my_fake_docker_registry_client.get_image_tags(image="fake-no-tags"),
            second=[],
        )
        self.assertEqual(
            first=my_fake_docker_registry_client.get_image_tags(image="fake-alpine"),
            second=["fake-alpine:a", "fake-alpine:b", "fake-alpine:c"],
        )

    @patch(
        target="docker_registry_client.HTTPSConnection",
        new=MagicMock(return_value=FakeHTTPSConnection(status=404)),
    )
    def test_request_404(self):
        """Docker Client Get Image Tags Image Not Found (404)"""

        my_fake_docker_registry_client: DockerRegistryClient = DockerRegistryClient(
            registry_url="https://fake.registry.example.com:12345"
        )
        with self.assertRaises(expected_exception=HTTPException):
            my_fake_docker_registry_client.get_image_tags(image="pouet")

    @patch(
        target="docker_registry_client.HTTPSConnection",
        new=MagicMock(
            return_value=FakeHTTPSConnection(
                status=301, headers={"location": "/v2/_catalog"}
            )
        ),
    )
    def test_request_301(self):
        """Docker Client Get Images (301)"""

        my_fake_docker_registry_client: DockerRegistryClient = DockerRegistryClient(
            registry_url="https://fake.registry.example.com:12345/"
        )

        self.assertEqual(
            first=my_fake_docker_registry_client.get_images(),
            second=["fake-alpine", "fake-ubuntu", "fake-python"],
        )
