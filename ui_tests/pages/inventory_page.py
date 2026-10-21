"""Page object for the SauceDemo product inventory page."""

from __future__ import annotations

import re

from playwright.sync_api import Page, expect


class InventoryPage:
    URL_FRAGMENT = "/inventory.html"

    def __init__(self, page: Page) -> None:
        self.page = page
        self.title = page.locator('[data-test="title"]')
        self.items = page.locator(".inventory_item")
        self.sort_select = page.locator('[data-test="product-sort-container"]')
        self.cart_link = page.locator('[data-test="shopping-cart-link"]')
        self.cart_badge = page.locator('[data-test="shopping-cart-badge"]')

    def wait_until_loaded(self) -> None:
        expect(self.title).to_have_text("Products")
        expect(self.items.first).to_be_visible()

    def product_names(self) -> list[str]:
        return self.page.locator(".inventory_item_name").all_inner_texts()

    def product_prices(self) -> list[float]:
        price_texts = self.page.locator(".inventory_item_price").all_inner_texts()
        return [float(re.sub(r"[^0-9.]", "", text)) for text in price_texts]

    def sort_by(self, value: str) -> None:
        self.sort_select.select_option(value)

    def add_product(self, product_slug: str) -> None:
        self.page.locator(f'[data-test="add-to-cart-{product_slug}"]').click()

    def remove_product(self, product_slug: str) -> None:
        self.page.locator(f'[data-test="remove-{product_slug}"]').click()

    def cart_count(self) -> int:
        if self.cart_badge.count() == 0:
            return 0
        return int(self.cart_badge.inner_text())

    def open_cart(self) -> None:
        self.cart_link.click()

    def logout(self) -> None:
        self.page.locator("#react-burger-menu-btn").click()
        logout_link = self.page.locator("#logout_sidebar_link")
        expect(logout_link).to_be_visible()
        logout_link.click()
