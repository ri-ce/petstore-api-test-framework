"""Shopping cart and checkout tests."""

from __future__ import annotations

import pytest
from playwright.sync_api import expect

from ui_tests.pages.cart_page import CartPage
from ui_tests.pages.checkout_page import CheckoutPage
from ui_tests.pages.inventory_page import InventoryPage
from ui_tests.pages.login_page import LoginPage


BACKPACK_SLUG = "sauce-labs-backpack"
BACKPACK_NAME = "Sauce Labs Backpack"


def _open_inventory(page) -> InventoryPage:
    login_page = LoginPage(page)
    login_page.open()
    login_page.login("standard_user", "secret_sauce")
    inventory_page = InventoryPage(page)
    inventory_page.wait_until_loaded()
    return inventory_page


@pytest.mark.ui
@pytest.mark.smoke
def test_add_and_remove_product_updates_cart_badge(page):
    inventory_page = _open_inventory(page)

    inventory_page.add_product(BACKPACK_SLUG)
    assert inventory_page.cart_count() == 1

    inventory_page.remove_product(BACKPACK_SLUG)
    assert inventory_page.cart_count() == 0


@pytest.mark.ui
def test_selected_product_is_shown_in_cart(page):
    inventory_page = _open_inventory(page)
    inventory_page.add_product(BACKPACK_SLUG)
    inventory_page.open_cart()

    cart_page = CartPage(page)
    cart_page.wait_until_loaded()
    assert cart_page.item_names() == [BACKPACK_NAME]


@pytest.mark.ui
def test_checkout_requires_customer_information(page):
    inventory_page = _open_inventory(page)
    inventory_page.add_product(BACKPACK_SLUG)
    inventory_page.open_cart()

    cart_page = CartPage(page)
    cart_page.wait_until_loaded()
    cart_page.checkout()

    checkout_page = CheckoutPage(page)
    checkout_page.continue_without_information()
    expect(checkout_page.error_message).to_contain_text(
        "First Name is required"
    )


@pytest.mark.ui
@pytest.mark.smoke
def test_standard_user_can_complete_checkout(page):
    inventory_page = _open_inventory(page)
    inventory_page.add_product(BACKPACK_SLUG)
    inventory_page.open_cart()

    cart_page = CartPage(page)
    cart_page.wait_until_loaded()
    cart_page.checkout()

    checkout_page = CheckoutPage(page)
    checkout_page.fill_customer_information(
        "Test",
        "User",
        "200000",
    )
    checkout_page.finish()

    assert checkout_page.order_is_complete()
