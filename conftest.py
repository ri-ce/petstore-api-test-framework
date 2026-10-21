"""Shared fixtures for starting the demo service and preparing test data."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from copy import deepcopy
from pathlib import Path
from typing import Iterator

import pytest
import requests

from api.client import CampusMartClient


PROJECT_ROOT = Path(__file__).resolve().parent
TEST_DATA = json.loads(
    (PROJECT_ROOT / "data" / "test_data.json").read_text(encoding="utf-8")
)


def _unused_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.fixture(scope="session")
def base_url() -> Iterator[str]:
    port = _unused_port()
    url = f"http://127.0.0.1:{port}"
    env = os.environ.copy()
    env["DEMO_MODE"] = "1"
    env["PYTHONPATH"] = str(PROJECT_ROOT)
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "app.server",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=PROJECT_ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )

    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(
                f"Demo API exited unexpectedly with code {process.returncode}"
            )
        try:
            response = requests.get(f"{url}/health", timeout=0.5)
            if response.status_code == 200:
                break
        except requests.RequestException:
            time.sleep(0.1)
    else:
        process.terminate()
        raise RuntimeError("Demo API did not become ready within 10 seconds")

    yield url

    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


@pytest.fixture(autouse=True)
def clean_state(base_url: str) -> None:
    response = requests.post(
        f"{base_url}/api/admin/reset",
        timeout=3,
    )
    assert response.status_code == 200, response.text


@pytest.fixture
def client_factory(base_url: str) -> Iterator[callable]:
    clients: list[CampusMartClient] = []

    def factory() -> CampusMartClient:
        client = CampusMartClient(base_url)
        clients.append(client)
        return client

    yield factory
    for client in clients:
        client.close()


def _authenticated_client(
    client_factory: callable,
    user_key: str,
) -> CampusMartClient:
    client = client_factory()
    credentials = TEST_DATA["users"][user_key]
    response = client.auth.login(**credentials)
    assert response.status_code == 200, response.text
    return client


@pytest.fixture
def anonymous(client_factory: callable) -> CampusMartClient:
    return client_factory()


@pytest.fixture
def seller(client_factory: callable) -> CampusMartClient:
    return _authenticated_client(client_factory, "seller")


@pytest.fixture
def buyer(client_factory: callable) -> CampusMartClient:
    return _authenticated_client(client_factory, "buyer")


@pytest.fixture
def admin(client_factory: callable) -> CampusMartClient:
    return _authenticated_client(client_factory, "admin")


@pytest.fixture
def listing_payload() -> dict[str, object]:
    return deepcopy(TEST_DATA["listing"])


@pytest.fixture
def created_listing(
    seller: CampusMartClient,
    listing_payload: dict[str, object],
) -> dict[str, object]:
    response = seller.listings.create(listing_payload)
    return response.json()["data"]
