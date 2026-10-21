"""Page object for the SauceDemo shopping cart."""

from __future__ import annotations

from playwright.sync_api import Page, expect


class CartPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.title = page.locator('[data-test="title"]')
        self.cart_items = page.locator(".cart_item")
        self.checkout_button = page.locator('[data-test="checkout"]')

    def wait_until_loaded(self) -> None:
        expect(self.title).to_have_text("Your Cart")

    def item_names(self) -> list[str]:
        return self.page.locator(".inventory_item_name").all_inner_texts()

    def checkout(self) -> None:
        self.checkout_button.click()
