"""Pet CRUD and query tests against the real public API."""

from __future__ import annotations

import pytest


@pytest.mark.smoke
@pytest.mark.parametrize("status", ["available", "pending", "sold"])
def test_find_pets_by_status(client, status):
    response = client.pets.find_by_status(status)
    pets = response.json()

    assert isinstance(pets, list)
    if pets:
        assert all(pet["status"] == status for pet in pets)


@pytest.mark.smoke
def test_create_pet_returns_business_fields(client, pet_payload):
    response = client.pets.create(pet_payload)
    pet = response.json()

    assert pet["id"] == pet_payload["id"]
    assert pet["name"] == pet_payload["name"]
    assert pet["status"] == "available"
    assert pet["category"]["name"] == "automation"
    assert pet["tags"][0]["name"] == "api-test"

    client.pets.delete(pet["id"])


def test_get_created_pet(client, created_pet):
    response = client.pets.get(created_pet["id"])
    actual = response.json()

    assert actual["id"] == created_pet["id"]
    assert actual["name"] == created_pet["name"]
    assert actual["photoUrls"] == created_pet["photoUrls"]


def test_update_pet_and_read_back(client, created_pet):
    updated_payload = {
        **created_pet,
        "name": f"{created_pet['name']}-updated",
        "status": "pending",
    }
    updated = client.pets.update(updated_payload).json()

    assert updated["name"].endswith("-updated")
    assert updated["status"] == "pending"

    actual = client.pets.get(created_pet["id"]).json()
    assert actual["name"] == updated["name"]
    assert actual["status"] == "pending"


def test_delete_pet_then_get_returns_404(client, created_pet):
    client.pets.delete(created_pet["id"])
    response = client.pets.get(
        created_pet["id"],
        expected_status=404,
    )

    assert response.text.strip() == "Pet not found"


@pytest.mark.parametrize(
    ("pet_id", "expected_status"),
    [
        (987654321, 404),
        ("not-a-number", 400),
    ],
)
def test_missing_or_invalid_pet_is_rejected(
    client,
    pet_id,
    expected_status,
):
    response = client.pets.get(
        pet_id,
        expected_status=expected_status,
    )
    if expected_status == 400:
        assert "couldn't convert" in response.json()["message"]
