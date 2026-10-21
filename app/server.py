"""A small, intentionally self-contained API used by the test framework.

The service is an in-memory demo. It is not intended for production use:
passwords are stored in plain text and state is reset whenever the process
restarts. Keeping the API local makes the automated tests deterministic and
lets the project run without a public-network dependency.
"""

from __future__ import annotations

import argparse
import os
import secrets
import threading
import uuid
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable

from flask import Flask, g, jsonify, request


ALLOWED_CATEGORIES = {"books", "digital", "daily", "sports", "other"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def error_response(
    status: int,
    code: str,
    message: str,
    fields: dict[str, str] | None = None,
):
    error: dict[str, Any] = {"code": code, "message": message}
    if fields:
        error["fields"] = fields
    return jsonify({"error": error}), status


class Store:
    """Thread-safe in-memory persistence for the demo API."""

    def __init__(self) -> None:
        self.lock = threading.RLock()
        self.users: dict[str, dict[str, Any]] = {}
        self.listings: dict[str, dict[str, Any]] = {}
        self.orders: dict[str, dict[str, Any]] = {}
        self.tokens: dict[str, str] = {}
        self.reset()

    def reset(self) -> None:
        with self.lock:
            self.users = {
                "user-alice": {
                    "id": "user-alice",
                    "username": "alice",
                    "password": "Seller123!",
                    "display_name": "Alice",
                    "role": "seller",
                },
                "user-bob": {
                    "id": "user-bob",
                    "username": "bob",
                    "password": "Buyer123!",
                    "display_name": "Bob",
                    "role": "buyer",
                },
                "user-admin": {
                    "id": "user-admin",
                    "username": "admin",
                    "password": "Admin123!",
                    "display_name": "Administrator",
                    "role": "admin",
                },
            }
            self.tokens = {}
            self.orders = {}
            now = utc_now()
            self.listings = {
                "listing-calculator": {
                    "id": "listing-calculator",
                    "seller_id": "user-alice",
                    "title": "科学计算器",
                    "description": "九成新，功能正常",
                    "category": "digital",
                    "price": 35.0,
                    "stock": 1,
                    "status": "active",
                    "created_at": now,
                    "updated_at": now,
                },
                "listing-textbook": {
                    "id": "listing-textbook",
                    "seller_id": "user-alice",
                    "title": "软件测试基础教材",
                    "description": "含少量笔记",
                    "category": "books",
                    "price": 18.5,
                    "stock": 3,
                    "status": "active",
                    "created_at": now,
                    "updated_at": now,
                },
                "listing-lamp": {
                    "id": "listing-lamp",
                    "seller_id": "user-bob",
                    "title": "宿舍台灯",
                    "description": "三档亮度，可充电",
                    "category": "daily",
                    "price": 22.0,
                    "stock": 2,
                    "status": "active",
                    "created_at": now,
                    "updated_at": now,
                },
            }


def public_user(user: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": user["id"],
        "username": user["username"],
        "display_name": user["display_name"],
        "role": user["role"],
    }


def serialize_listing(listing: dict[str, Any]) -> dict[str, Any]:
    return dict(listing)


def serialize_order(order: dict[str, Any]) -> dict[str, Any]:
    return dict(order)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["JSON_AS_ASCII"] = False
    store = Store()

    def find_user_by_token() -> dict[str, Any] | None:
        authorization = request.headers.get("Authorization", "")
        if not authorization.startswith("Bearer "):
            return None
        token = authorization.removeprefix("Bearer ").strip()
        with store.lock:
            user_id = store.tokens.get(token)
            return store.users.get(user_id) if user_id else None

    def require_auth(view: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(view)
        def wrapper(*args: Any, **kwargs: Any):
            user = find_user_by_token()
            if user is None:
                return error_response(
                    401,
                    "UNAUTHORIZED",
                    "缺少有效的访问令牌",
                )
            g.current_user = user
            return view(*args, **kwargs)

        return wrapper

    def parse_json_object() -> tuple[dict[str, Any] | None, Any | None]:
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return None, error_response(
                400,
                "INVALID_JSON",
                "请求体必须是 JSON 对象",
            )
        return payload, None

    def validate_listing(
        payload: dict[str, Any],
        *,
        partial: bool = False,
    ) -> tuple[dict[str, Any], dict[str, str]]:
        fields: dict[str, str] = {}
        cleaned: dict[str, Any] = {}

        if not partial or "title" in payload:
            title = payload.get("title")
            if not isinstance(title, str) or not 2 <= len(title.strip()) <= 80:
                fields["title"] = "标题长度必须为 2 到 80 个字符"
            else:
                cleaned["title"] = title.strip()

        if not partial or "description" in payload:
            description = payload.get("description", "")
            if not isinstance(description, str) or len(description) > 500:
                fields["description"] = "描述必须是长度不超过 500 的字符串"
            else:
                cleaned["description"] = description.strip()

        if not partial or "category" in payload:
            category = payload.get("category")
            if category not in ALLOWED_CATEGORIES:
                fields["category"] = "商品分类不合法"
            else:
                cleaned["category"] = category

        if not partial or "price" in payload:
            price = payload.get("price")
            if (
                isinstance(price, bool)
                or not isinstance(price, (int, float))
                or not 0 < float(price) <= 100_000
            ):
                fields["price"] = "价格必须大于 0 且不超过 100000"
            else:
                cleaned["price"] = round(float(price), 2)

        if not partial or "stock" in payload:
            stock = payload.get("stock")
            if (
                isinstance(stock, bool)
                or not isinstance(stock, int)
                or not 0 <= stock <= 999
            ):
                fields["stock"] = "库存必须是 0 到 999 的整数"
            else:
                cleaned["stock"] = stock

        return cleaned, fields

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "service": "campusmart-demo-api"})

    @app.post("/api/admin/reset")
    def reset_demo_state():
        if os.getenv("DEMO_MODE") != "1":
            return error_response(404, "NOT_FOUND", "接口不存在")
        store.reset()
        return jsonify({"data": {"message": "演示数据已重置"}})

    @app.post("/api/auth/login")
    def login():
        payload, error = parse_json_object()
        if error:
            return error

        username = payload.get("username")
        password = payload.get("password")
        fields: dict[str, str] = {}
        if not isinstance(username, str) or not username.strip():
            fields["username"] = "用户名不能为空"
        if not isinstance(password, str) or not password:
            fields["password"] = "密码不能为空"
        if fields:
            return error_response(
                400,
                "VALIDATION_ERROR",
                "登录参数校验失败",
                fields,
            )

        with store.lock:
            user = next(
                (
                    item
                    for item in store.users.values()
                    if item["username"] == username.strip()
                ),
                None,
            )
            if user is None or user["password"] != password:
                return error_response(
                    401,
                    "INVALID_CREDENTIALS",
                    "用户名或密码错误",
                )
            token = secrets.token_urlsafe(24)
            store.tokens[token] = user["id"]

        return jsonify(
            {
                "data": {
                    "token": token,
                    "user": public_user(user),
                }
            }
        )

    @app.post("/api/auth/logout")
    @require_auth
    def logout():
        authorization = request.headers["Authorization"]
        token = authorization.removeprefix("Bearer ").strip()
        with store.lock:
            store.tokens.pop(token, None)
        return "", 204

    @app.get("/api/listings")
    def list_listings():
        try:
            min_price = float(request.args["min_price"])
            max_price = float(request.args["max_price"])
        except KeyError:
            min_price = 0.0
            max_price = float("inf")
        except ValueError:
            return error_response(
                400,
                "INVALID_FILTER",
                "价格筛选参数必须是数字",
            )

        if min_price < 0 or max_price < 0 or min_price > max_price:
            return error_response(
                400,
                "INVALID_FILTER",
                "价格筛选范围不合法",
            )

        category = request.args.get("category")
        if category and category not in ALLOWED_CATEGORIES:
            return error_response(
                400,
                "INVALID_FILTER",
                "商品分类不合法",
            )
        keyword = request.args.get("keyword", "").strip().lower()

        with store.lock:
            items = list(store.listings.values())

        items = [
            item
            for item in items
            if item["status"] == "active"
            and (not category or item["category"] == category)
            and min_price <= item["price"] <= max_price
            and (not keyword or keyword in item["title"].lower())
        ]
        items.sort(key=lambda item: (item["price"], item["title"]))
        data = [serialize_listing(item) for item in items]
        return jsonify({"data": data, "meta": {"count": len(data)}})

    @app.get("/api/listings/<listing_id>")
    def get_listing(listing_id: str):
        with store.lock:
            listing = store.listings.get(listing_id)
            if listing is None:
                return error_response(
                    404,
                    "LISTING_NOT_FOUND",
                    "商品不存在",
                )
            data = serialize_listing(listing)
        return jsonify({"data": data})

    @app.post("/api/listings")
    @require_auth
    def create_listing():
        payload, error = parse_json_object()
        if error:
            return error
        cleaned, fields = validate_listing(payload)
        if fields:
            return error_response(
                400,
                "VALIDATION_ERROR",
                "商品参数校验失败",
                fields,
            )
        if cleaned["stock"] < 1:
            return error_response(
                400,
                "VALIDATION_ERROR",
                "发布商品时库存必须大于 0",
                {"stock": "发布商品时库存必须大于 0"},
            )

        now = utc_now()
        listing = {
            "id": f"listing-{uuid.uuid4().hex[:10]}",
            "seller_id": g.current_user["id"],
            **cleaned,
            "status": "active",
            "created_at": now,
            "updated_at": now,
        }
        with store.lock:
            store.listings[listing["id"]] = listing
        return jsonify({"data": serialize_listing(listing)}), 201

    @app.patch("/api/listings/<listing_id>")
    @require_auth
    def update_listing(listing_id: str):
        payload, error = parse_json_object()
        if error:
            return error
        if not payload:
            return error_response(
                400,
                "VALIDATION_ERROR",
                "至少需要提供一个待更新字段",
            )
        cleaned, fields = validate_listing(payload, partial=True)
        unknown = set(payload) - {
            "title",
            "description",
            "category",
            "price",
            "stock",
        }
        if unknown:
            fields["_unknown"] = f"不支持字段: {', '.join(sorted(unknown))}"
        if fields:
            return error_response(
                400,
                "VALIDATION_ERROR",
                "商品参数校验失败",
                fields,
            )

        with store.lock:
            listing = store.listings.get(listing_id)
            if listing is None:
                return error_response(
                    404,
                    "LISTING_NOT_FOUND",
                    "商品不存在",
                )
            if (
                listing["seller_id"] != g.current_user["id"]
                and g.current_user["role"] != "admin"
            ):
                return error_response(
                    403,
                    "FORBIDDEN",
                    "只能修改自己发布的商品",
                )
            listing.update(cleaned)
            listing["updated_at"] = utc_now()
            listing["status"] = "active" if listing["stock"] > 0 else "sold_out"
            data = serialize_listing(listing)
        return jsonify({"data": data})

    @app.delete("/api/listings/<listing_id>")
    @require_auth
    def delete_listing(listing_id: str):
        with store.lock:
            listing = store.listings.get(listing_id)
            if listing is None:
                return error_response(
                    404,
                    "LISTING_NOT_FOUND",
                    "商品不存在",
                )
            if (
                listing["seller_id"] != g.current_user["id"]
                and g.current_user["role"] != "admin"
            ):
                return error_response(
                    403,
                    "FORBIDDEN",
                    "只能删除自己发布的商品",
                )
            has_pending_order = any(
                order["listing_id"] == listing_id
                and order["status"] == "pending"
                for order in store.orders.values()
            )
            if has_pending_order:
                return error_response(
                    409,
                    "LISTING_HAS_PENDING_ORDER",
                    "商品存在待处理订单，暂不能删除",
                )
            del store.listings[listing_id]
        return "", 204

    @app.post("/api/orders")
    @require_auth
    def create_order():
        payload, error = parse_json_object()
        if error:
            return error
        listing_id = payload.get("listing_id")
        quantity = payload.get("quantity")
        fields: dict[str, str] = {}
        if not isinstance(listing_id, str) or not listing_id:
            fields["listing_id"] = "商品 ID 不能为空"
        if (
            isinstance(quantity, bool)
            or not isinstance(quantity, int)
            or quantity < 1
        ):
            fields["quantity"] = "购买数量必须是正整数"
        if fields:
            return error_response(
                400,
                "VALIDATION_ERROR",
                "订单参数校验失败",
                fields,
            )

        with store.lock:
            listing = store.listings.get(listing_id)
            if listing is None or listing["status"] != "active":
                return error_response(
                    404,
                    "LISTING_NOT_FOUND",
                    "可购买的商品不存在",
                )
            if listing["seller_id"] == g.current_user["id"]:
                return error_response(
                    409,
                    "SELF_PURCHASE",
                    "不能购买自己发布的商品",
                )
            if quantity > listing["stock"]:
                return error_response(
                    409,
                    "INSUFFICIENT_STOCK",
                    "商品库存不足",
                )

            listing["stock"] -= quantity
            listing["status"] = "active" if listing["stock"] else "sold_out"
            listing["updated_at"] = utc_now()
            order = {
                "id": f"order-{uuid.uuid4().hex[:10]}",
                "listing_id": listing_id,
                "buyer_id": g.current_user["id"],
                "seller_id": listing["seller_id"],
                "quantity": quantity,
                "unit_price": listing["price"],
                "total_price": round(listing["price"] * quantity, 2),
                "status": "pending",
                "created_at": utc_now(),
                "cancelled_at": None,
            }
            store.orders[order["id"]] = order
            data = serialize_order(order)
        return jsonify({"data": data}), 201

    @app.get("/api/orders/<order_id>")
    @require_auth
    def get_order(order_id: str):
        with store.lock:
            order = store.orders.get(order_id)
            if order is None:
                return error_response(
                    404,
                    "ORDER_NOT_FOUND",
                    "订单不存在",
                )
            if g.current_user["id"] not in {
                order["buyer_id"],
                order["seller_id"],
            } and g.current_user["role"] != "admin":
                return error_response(
                    403,
                    "FORBIDDEN",
                    "无权查看该订单",
                )
            data = serialize_order(order)
        return jsonify({"data": data})

    @app.post("/api/orders/<order_id>/cancel")
    @require_auth
    def cancel_order(order_id: str):
        with store.lock:
            order = store.orders.get(order_id)
            if order is None:
                return error_response(
                    404,
                    "ORDER_NOT_FOUND",
                    "订单不存在",
                )
            if order["buyer_id"] != g.current_user["id"]:
                return error_response(
                    403,
                    "FORBIDDEN",
                    "只能取消自己购买的订单",
                )
            if order["status"] != "pending":
                return error_response(
                    409,
                    "ORDER_NOT_CANCELLABLE",
                    "当前订单状态不允许取消",
                )
            order["status"] = "cancelled"
            order["cancelled_at"] = utc_now()
            listing = store.listings[order["listing_id"]]
            listing["stock"] += order["quantity"]
            listing["status"] = "active"
            listing["updated_at"] = utc_now()
            data = serialize_order(order)
        return jsonify({"data": data})

    return app


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the CampusMart demo API")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    app = create_app()
    app.run(
        host=args.host,
        port=args.port,
        debug=False,
        use_reloader=False,
    )


if __name__ == "__main__":
    main()
