"""Authentication and session tests."""

from __future__ import annotations

import pytest


@pytest.mark.smoke
def test_health_check(anonymous):
    response = anonymous.request("GET", "/health", expected_status=200)
    assert response.json()["status"] == "ok"


@pytest.mark.smoke
def test_login_returns_token_and_public_user(anonymous):
    response = anonymous.auth.login("alice", "Seller123!")

    data = response.json()["data"]
    assert data["token"]
    assert data["user"] == {
        "id": "user-alice",
        "username": "alice",
        "display_name": "Alice",
        "role": "seller",
    }
    assert "password" not in data["user"]


def test_login_rejects_wrong_password(anonymous):
    response = anonymous.auth.login(
        "alice",
        "wrong-password",
        expected_status=401,
    )
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


@pytest.mark.parametrize(
    ("username", "password", "field"),
    [
        ("", "Seller123!", "username"),
        ("alice", "", "password"),
        (None, None, "username"),
    ],
)
def test_login_validates_required_fields(
    anonymous,
    username,
    password,
    field,
):
    response = anonymous.auth.login(
        username,
        password,
        expected_status=400,
    )
    assert field in response.json()["error"]["fields"]


def test_login_rejects_non_json_body(anonymous):
    response = anonymous.request(
        "POST",
        "/api/auth/login",
        data="username=alice",
        headers={"Content-Type": "text/plain"},
        expected_status=400,
    )
    assert response.json()["error"]["code"] == "INVALID_JSON"


@pytest.mark.smoke
def test_logout_invalidates_current_token(seller):
    seller.auth.logout()
    response = seller.listings.create(
        {
            "title": "退出后创建的商品",
            "category": "other",
            "price": 1,
            "stock": 1,
        },
        expected_status=401,
    )
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_protected_endpoint_requires_token(anonymous):
    response = anonymous.listings.create(
        {
            "title": "未登录商品",
            "category": "other",
            "price": 10,
            "stock": 1,
        },
        expected_status=401,
    )
    assert response.json()["error"]["code"] == "UNAUTHORIZED"
