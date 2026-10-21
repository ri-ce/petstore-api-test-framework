"""HTTP client and service layer for the public Swagger Petstore API."""

from __future__ import annotations

import logging
import os
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


logger = logging.getLogger(__name__)
DEFAULT_BASE_URL = "https://petstore3.swagger.io/api/v3"


class PetstoreClient:
    """Service-oriented API client with retry and request logging."""

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float = 20.0,
    ) -> None:
        self.base_url = (
            base_url
            or os.getenv("PETSTORE_BASE_URL")
            or DEFAULT_BASE_URL
        ).rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

        retry = Retry(
            total=3,
            connect=3,
            read=3,
            status=3,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=None,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        self.system = SystemService(self)
        self.pets = PetService(self)
        self.store = StoreService(self)

    def request(
        self,
        method: str,
        path: str,
        *,
        expected_status: int | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        response = self.session.request(
            method,
            f"{self.base_url}{path}",
            timeout=self.timeout,
            **kwargs,
        )
        logger.info(
            "%s %s -> %s",
            method.upper(),
            path,
            response.status_code,
        )
        if (
            expected_status is not None
            and response.status_code != expected_status
        ):
            raise AssertionError(
                f"{method.upper()} {path} expected HTTP {expected_status}, "
                f"got {response.status_code}: {response.text[:500]}"
            )
        return response

    def close(self) -> None:
        self.session.close()


class SystemService:
    def __init__(self, client: PetstoreClient) -> None:
        self.client = client

    def openapi(self) -> requests.Response:
        return self.client.request(
            "GET",
            "/openapi.json",
            expected_status=200,
        )


class PetService:
    def __init__(self, client: PetstoreClient) -> None:
        self.client = client

    def find_by_status(self, status: str) -> requests.Response:
        return self.client.request(
            "GET",
            "/pet/findByStatus",
            params={"status": status},
            expected_status=200,
        )

    def create(
        self,
        payload: dict[str, Any],
        *,
        expected_status: int = 200,
    ) -> requests.Response:
        return self.client.request(
            "POST",
            "/pet",
            json=payload,
            expected_status=expected_status,
        )

    def get(
        self,
        pet_id: int | str,
        *,
        expected_status: int = 200,
    ) -> requests.Response:
        return self.client.request(
            "GET",
            f"/pet/{pet_id}",
            expected_status=expected_status,
        )

    def update(
        self,
        payload: dict[str, Any],
        *,
        expected_status: int = 200,
    ) -> requests.Response:
        return self.client.request(
            "PUT",
            "/pet",
            json=payload,
            expected_status=expected_status,
        )

    def delete(
        self,
        pet_id: int | str,
        *,
        expected_status: int | None = 200,
    ) -> requests.Response:
        return self.client.request(
            "DELETE",
            f"/pet/{pet_id}",
            expected_status=expected_status,
        )


class StoreService:
    def __init__(self, client: PetstoreClient) -> None:
        self.client = client

    def inventory(self) -> requests.Response:
        return self.client.request(
            "GET",
            "/store/inventory",
            expected_status=200,
        )

    def create_order(
        self,
        payload: dict[str, Any],
        *,
        expected_status: int = 200,
    ) -> requests.Response:
        return self.client.request(
            "POST",
            "/store/order",
            json=payload,
            expected_status=expected_status,
        )

    def get_order(
        self,
        order_id: int | str,
        *,
        expected_status: int = 200,
    ) -> requests.Response:
        return self.client.request(
            "GET",
            f"/store/order/{order_id}",
            expected_status=expected_status,
        )

    def delete_order(
        self,
        order_id: int | str,
        *,
        expected_status: int | None = 200,
    ) -> requests.Response:
        return self.client.request(
            "DELETE",
            f"/store/order/{order_id}",
            expected_status=expected_status,
        )
