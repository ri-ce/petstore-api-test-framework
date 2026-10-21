"""Order creation, cancellation and stock consistency tests."""

from __future__ import annotations

import pytest


@pytest.mark.smoke
def test_buyer_can_create_order_and_stock_decreases(
    buyer,
    created_listing,
):
    response = buyer.orders.create(created_listing["id"], 2)
    order = response.json()["data"]

    assert order["buyer_id"] == "user-bob"
    assert order["seller_id"] == "user-alice"
    assert order["status"] == "pending"
    assert order["quantity"] == 2
    assert order["total_price"] == pytest.approx(199.0)

    listing = buyer.listings.get(created_listing["id"]).json()["data"]
    assert listing["stock"] == 2


def test_seller_cannot_buy_own_listing(seller, created_listing):
    response = seller.orders.create(
        created_listing["id"],
        1,
        expected_status=409,
    )
    assert response.json()["error"]["code"] == "SELF_PURCHASE"


def test_order_rejects_insufficient_stock(
    buyer,
    created_listing,
):
    response = buyer.orders.create(
        created_listing["id"],
        5,
        expected_status=409,
    )
    assert response.json()["error"]["code"] == "INSUFFICIENT_STOCK"


@pytest.mark.parametrize("quantity", [0, -1, 1.5, True])
def test_order_rejects_invalid_quantity(
    buyer,
    created_listing,
    quantity,
):
    response = buyer.orders.create(
        created_listing["id"],
        quantity,
        expected_status=400,
    )
    assert "quantity" in response.json()["error"]["fields"]


def test_order_rejects_missing_listing(buyer):
    response = buyer.orders.create(
        "listing-not-exist",
        1,
        expected_status=404,
    )
    assert response.json()["error"]["code"] == "LISTING_NOT_FOUND"


@pytest.mark.smoke
def test_buyer_and_seller_can_view_order(
    buyer,
    seller,
    created_listing,
):
    order = buyer.orders.create(
        created_listing["id"],
        1,
    ).json()["data"]

    buyer_view = buyer.orders.get(order["id"]).json()["data"]
    seller_view = seller.orders.get(order["id"]).json()["data"]
    assert buyer_view == seller_view


def test_get_missing_order_returns_404(buyer):
    response = buyer.orders.get(
        "order-not-exist",
        expected_status=404,
    )
    assert response.json()["error"]["code"] == "ORDER_NOT_FOUND"


def test_seller_cannot_cancel_buyer_order(
    buyer,
    seller,
    created_listing,
):
    order = buyer.orders.create(
        created_listing["id"],
        1,
    ).json()["data"]
    response = seller.orders.cancel(
        order["id"],
        expected_status=403,
    )
    assert response.json()["error"]["code"] == "FORBIDDEN"


@pytest.mark.smoke
def test_buyer_cancel_restores_stock(buyer, created_listing):
    original_stock = created_listing["stock"]
    order = buyer.orders.create(
        created_listing["id"],
        3,
    ).json()["data"]

    cancelled = buyer.orders.cancel(order["id"]).json()["data"]
    assert cancelled["status"] == "cancelled"
    assert cancelled["cancelled_at"]

    listing = buyer.listings.get(created_listing["id"]).json()["data"]
    assert listing["stock"] == original_stock
    assert listing["status"] == "active"


def test_order_cannot_be_cancelled_twice(
    buyer,
    created_listing,
):
    order = buyer.orders.create(
        created_listing["id"],
        1,
    ).json()["data"]
    buyer.orders.cancel(order["id"])

    response = buyer.orders.cancel(
        order["id"],
        expected_status=409,
    )
    assert response.json()["error"]["code"] == "ORDER_NOT_CANCELLABLE"


def test_listing_cannot_be_deleted_with_pending_order(
    buyer,
    seller,
    created_listing,
):
    buyer.orders.create(created_listing["id"], 1)
    response = seller.listings.delete(
        created_listing["id"],
        expected_status=409,
    )
    assert (
        response.json()["error"]["code"]
        == "LISTING_HAS_PENDING_ORDER"
    )


def test_sold_out_listing_cannot_be_ordered(
    buyer,
    created_listing,
):
    buyer.orders.create(
        created_listing["id"],
        created_listing["stock"],
    )
    listing = buyer.listings.get(created_listing["id"]).json()["data"]
    assert listing["status"] == "sold_out"
    assert listing["stock"] == 0

    response = buyer.orders.create(
        created_listing["id"],
        1,
        expected_status=404,
    )
    assert response.json()["error"]["code"] == "LISTING_NOT_FOUND"

    listed_ids = {
        item["id"]
        for item in buyer.listings.list().json()["data"]
    }
    assert created_listing["id"] not in listed_ids
