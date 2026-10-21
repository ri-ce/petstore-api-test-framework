"""Store inventory and order lifecycle tests."""

from __future__ import annotations

import pytest


@pytest.mark.smoke
def test_inventory_returns_status_map(client):
    response = client.store.inventory()
    inventory = response.json()

    assert isinstance(inventory, dict)
    assert inventory
    assert all(isinstance(value, int) for value in inventory.values())


@pytest.mark.smoke
def test_create_order_returns_expected_fields(client, order_payload):
    response = client.store.create_order(order_payload)
    order = response.json()

    assert order["id"] == order_payload["id"]
    assert order["petId"] == order_payload["petId"]
    assert order["quantity"] == 1
    assert order["status"] == "placed"
    assert order["complete"] is False


def test_get_created_order(client, created_order):
    response = client.store.get_order(created_order["id"])
    assert response.json() == created_order


def test_delete_order_then_get_returns_404(client, created_order):
    client.store.delete_order(created_order["id"])
    response = client.store.get_order(
        created_order["id"],
        expected_status=404,
    )

    assert response.status_code == 404
    assert response.text.strip() == "Order not found"


def test_missing_order_returns_404(client):
    client.store.get_order(
        999_999_999,
        expected_status=404,
    )
