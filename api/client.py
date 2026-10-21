"""HTTP client and service objects used by the test suite."""

from __future__ import annotations

import logging
from typing import Any

import requests


logger = logging.getLogger(__name__)


class CampusMartClient:
    """Small service-oriented wrapper around requests.Session."""

    def __init__(self, base_url: str, timeout: float = 5.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        self.auth = AuthService(self)
        self.listings = ListingsService(self)
        self.orders = OrdersService(self)

    def set_token(self, token: str) -> None:
        self.session.headers["Authorization"] = f"Bearer {token}"

    def clear_token(self) -> None:
        self.session.headers.pop("Authorization", None)

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
                f"got {response.status_code}: {response.text}"
            )
        return response

    def close(self) -> None:
        self.session.close()


class AuthService:
    def __init__(self, client: CampusMartClient) -> None:
        self.client = client

    def login(
        self,
        username: Any,
        password: Any,
        *,
        expected_status: int | None = 200,
    ) -> requests.Response:
        response = self.client.request(
            "POST",
            "/api/auth/login",
            expected_status=expected_status,
            json={"username": username, "password": password},
        )
        if response.status_code == 200:
            self.client.set_token(response.json()["data"]["token"])
        return response

    def logout(self) -> requests.Response:
        response = self.client.request(
            "POST",
            "/api/auth/logout",
            expected_status=204,
        )
        self.client.clear_token()
        return response


class ListingsService:
    def __init__(self, client: CampusMartClient) -> None:
        self.client = client

    def list(self, **params: Any) -> requests.Response:
        return self.client.request(
            "GET",
            "/api/listings",
            params=params,
            expected_status=200,
        )

    def get(
        self,
        listing_id: str,
        *,
        expected_status: int = 200,
    ) -> requests.Response:
        return self.client.request(
            "GET",
            f"/api/listings/{listing_id}",
            expected_status=expected_status,
        )

    def create(
        self,
        payload: dict[str, Any],
        *,
        expected_status: int = 201,
    ) -> requests.Response:
        return self.client.request(
            "POST",
            "/api/listings",
            json=payload,
            expected_status=expected_status,
        )

    def update(
        self,
        listing_id: str,
        payload: dict[str, Any],
        *,
        expected_status: int = 200,
    ) -> requests.Response:
        return self.client.request(
            "PATCH",
            f"/api/listings/{listing_id}",
            json=payload,
            expected_status=expected_status,
        )

    def delete(
        self,
        listing_id: str,
        *,
        expected_status: int = 204,
    ) -> requests.Response:
        return self.client.request(
            "DELETE",
            f"/api/listings/{listing_id}",
            expected_status=expected_status,
        )


class OrdersService:
    def __init__(self, client: CampusMartClient) -> None:
        self.client = client

    def create(
        self,
        listing_id: str,
        quantity: int,
        *,
        expected_status: int = 201,
    ) -> requests.Response:
        return self.client.request(
            "POST",
            "/api/orders",
            json={"listing_id": listing_id, "quantity": quantity},
            expected_status=expected_status,
        )

    def get(
        self,
        order_id: str,
        *,
        expected_status: int = 200,
    ) -> requests.Response:
        return self.client.request(
            "GET",
            f"/api/orders/{order_id}",
            expected_status=expected_status,
        )

    def cancel(
        self,
        order_id: str,
        *,
        expected_status: int = 200,
    ) -> requests.Response:
        return self.client.request(
            "POST",
            f"/api/orders/{order_id}/cancel",
            expected_status=expected_status,
        )
