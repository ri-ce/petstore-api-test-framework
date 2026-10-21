"""Product catalog and sorting tests."""

from __future__ import annotations

import pytest

from ui_tests.pages.inventory_page import InventoryPage
from ui_tests.pages.login_page import LoginPage


def _log_in(page) -> InventoryPage:
    login_page = LoginPage(page)
    login_page.open()
    login_page.login("standard_user", "secret_sauce")
    inventory_page = InventoryPage(page)
    inventory_page.wait_until_loaded()
    return inventory_page


@pytest.mark.ui
@pytest.mark.smoke
def test_inventory_displays_all_products(page):
    inventory_page = _log_in(page)

    assert inventory_page.items.count() == 6
    assert len(inventory_page.product_names()) == 6


@pytest.mark.ui
def test_products_can_be_sorted_by_price_low_to_high(page):
    inventory_page = _log_in(page)
    inventory_page.sort_by("lohi")

    prices = inventory_page.product_prices()
    assert prices == sorted(prices)


@pytest.mark.ui
def test_products_can_be_sorted_by_name_z_to_a(page):
    inventory_page = _log_in(page)
    inventory_page.sort_by("za")

    names = inventory_page.product_names()
    assert names == sorted(names, reverse=True)
