"""OpenAPI contract checks for the public Petstore service."""

from __future__ import annotations

import pytest


@pytest.mark.smoke
def test_openapi_document_is_available(client):
    response = client.system.openapi()
    document = response.json()

    assert document["openapi"].startswith("3.")
    assert document["info"]["title"]
    assert response.headers["Content-Type"].startswith("application/json")


@pytest.mark.parametrize(
    "path",
    [
        "/pet",
        "/pet/{petId}",
        "/pet/findByStatus",
        "/store/inventory",
        "/store/order",
        "/store/order/{orderId}",
    ],
)
def test_openapi_contains_required_business_paths(client, path):
    document = client.system.openapi().json()
    assert path in document["paths"]


def test_openapi_documents_crud_methods(client):
    document = client.system.openapi().json()
    pet_path = document["paths"]["/pet"]
    order_path = document["paths"]["/store/order"]

    assert {"post", "put"} <= set(pet_path)
    assert "post" in order_path
