"""Fixtures for testing the public Swagger Petstore API."""

from __future__ import annotations

import json
import secrets
from copy import deepcopy
from pathlib import Path
from typing import Iterator

import pytest
import requests

from api.client import PetstoreClient


PROJECT_ROOT = Path(__file__).resolve().parent
TEST_DATA = json.loads(
    (PROJECT_ROOT / "data" / "test_data.json").read_text(encoding="utf-8")
)


@pytest.fixture
def client() -> Iterator[PetstoreClient]:
    api = PetstoreClient()
    yield api
    api.close()


@pytest.fixture
def unique_id() -> int:
    """Return a low-collision integer that fits the Petstore int64 ID."""
    return 1_000_000 + secrets.randbelow(900_000_000)


@pytest.fixture
def pet_payload(unique_id: int) -> dict[str, object]:
    payload = deepcopy(TEST_DATA["pet"])
    payload["id"] = unique_id
    return payload


@pytest.fixture
def created_pet(
    client: PetstoreClient,
    pet_payload: dict[str, object],
) -> Iterator[dict[str, object]]:
    response = client.pets.create(pet_payload)
    pet = response.json()
    try:
        yield pet
    finally:
        try:
            client.pets.delete(pet["id"], expected_status=None)
        except requests.RequestException:
            pass


@pytest.fixture
def order_payload(created_pet: dict[str, object]) -> dict[str, object]:
    payload = deepcopy(TEST_DATA["order"])
    payload["id"] = int(created_pet["id"]) + 1_000_000_000
    payload["petId"] = created_pet["id"]
    return payload


@pytest.fixture
def created_order(
    client: PetstoreClient,
    order_payload: dict[str, object],
) -> Iterator[dict[str, object]]:
    response = client.store.create_order(order_payload)
    order = response.json()
    try:
        yield order
    finally:
        try:
            client.store.delete_order(order["id"], expected_status=None)
        except requests.RequestException:
            pass
