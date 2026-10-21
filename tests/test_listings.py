"""Product listing, filtering and permission tests."""

from __future__ import annotations

import pytest


@pytest.mark.smoke
def test_list_returns_seeded_products(anonymous):
    response = anonymous.listings.list()
    data = response.json()["data"]

    assert response.json()["meta"]["count"] == 3
    assert {item["id"] for item in data} == {
        "listing-calculator",
        "listing-textbook",
        "listing-lamp",
    }


@pytest.mark.parametrize(
    ("params", "expected_ids"),
    [
        ({"category": "books"}, {"listing-textbook"}),
        ({"min_price": 20, "max_price": 30}, {"listing-lamp"}),
        ({"keyword": "台灯"}, {"listing-lamp"}),
        ({"keyword": "不存在"}, set()),
    ],
)
def test_listing_filters(anonymous, params, expected_ids):
    response = anonymous.listings.list(**params)
    actual_ids = {item["id"] for item in response.json()["data"]}
    assert actual_ids == expected_ids


@pytest.mark.parametrize(
    "params",
    [
        {"category": "unknown"},
        {"min_price": "abc"},
        {"min_price": 30, "max_price": 20},
    ],
)
def test_listing_rejects_invalid_filters(anonymous, params):
    client = anonymous
    response = client.request(
        "GET",
        "/api/listings",
        params=params,
        expected_status=400,
    )
    assert response.json()["error"]["code"] == "INVALID_FILTER"


def test_get_single_listing(anonymous):
    response = anonymous.listings.get("listing-textbook")
    data = response.json()["data"]

    assert data["title"] == "软件测试基础教材"
    assert data["seller_id"] == "user-alice"


def test_get_missing_listing_returns_404(anonymous):
    response = anonymous.listings.get(
        "listing-not-exist",
        expected_status=404,
    )
    assert response.json()["error"]["code"] == "LISTING_NOT_FOUND"


@pytest.mark.smoke
def test_seller_can_create_listing(seller, listing_payload):
    response = seller.listings.create(listing_payload)
    data = response.json()["data"]

    assert data["id"].startswith("listing-")
    assert data["seller_id"] == "user-alice"
    assert data["title"] == listing_payload["title"]
    assert data["status"] == "active"
    assert data["created_at"]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("title", "短"),
        ("title", ""),
        ("category", "invalid"),
        ("price", 0),
        ("price", -1),
        ("price", "99"),
        ("stock", -1),
        ("stock", 1000),
        ("stock", 1.5),
    ],
)
def test_create_listing_rejects_invalid_fields(
    seller,
    listing_payload,
    field,
    value,
):
    listing_payload[field] = value
    response = seller.listings.create(
        listing_payload,
        expected_status=400,
    )

    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert field in error["fields"]


def test_create_listing_rejects_zero_stock(
    seller,
    listing_payload,
):
    listing_payload["stock"] = 0
    response = seller.listings.create(
        listing_payload,
        expected_status=400,
    )
    assert "stock" in response.json()["error"]["fields"]


def test_seller_can_update_own_listing(
    seller,
    created_listing,
):
    response = seller.listings.update(
        created_listing["id"],
        {"price": 88, "stock": 6},
    )
    data = response.json()["data"]

    assert data["price"] == 88
    assert data["stock"] == 6
    assert data["updated_at"] >= created_listing["updated_at"]


def test_buyer_cannot_update_seller_listing(
    buyer,
    created_listing,
):
    response = buyer.listings.update(
        created_listing["id"],
        {"price": 1},
        expected_status=403,
    )
    assert response.json()["error"]["code"] == "FORBIDDEN"


def test_update_rejects_empty_body(seller, created_listing):
    response = seller.listings.update(
        created_listing["id"],
        {},
        expected_status=400,
    )
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_update_missing_listing_returns_404(seller):
    response = seller.listings.update(
        "listing-not-exist",
        {"price": 20},
        expected_status=404,
    )
    assert response.json()["error"]["code"] == "LISTING_NOT_FOUND"


def test_seller_can_delete_own_listing(seller, created_listing):
    seller.listings.delete(created_listing["id"])
    seller.listings.get(
        created_listing["id"],
        expected_status=404,
    )


def test_buyer_cannot_delete_seller_listing(
    buyer,
    created_listing,
):
    response = buyer.listings.delete(
        created_listing["id"],
        expected_status=403,
    )
    assert response.json()["error"]["code"] == "FORBIDDEN"


def test_admin_can_delete_listing(admin, created_listing):
    admin.listings.delete(created_listing["id"])
    created_listing_after = admin.listings.get(
        created_listing["id"],
        expected_status=404,
    )
    assert (
        created_listing_after.json()["error"]["code"]
        == "LISTING_NOT_FOUND"
    )


def test_delete_missing_listing_returns_404(seller):
    response = seller.listings.delete(
        "listing-not-exist",
        expected_status=404,
    )
    assert response.json()["error"]["code"] == "LISTING_NOT_FOUND"
