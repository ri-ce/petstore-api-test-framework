"""Page objects for the SauceDemo checkout flow."""

from __future__ import annotations

from playwright.sync_api import Page, expect


class CheckoutPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.first_name = page.locator('[data-test="firstName"]')
        self.last_name = page.locator('[data-test="lastName"]')
        self.postal_code = page.locator('[data-test="postalCode"]')
        self.continue_button = page.locator('[data-test="continue"]')
        self.finish_button = page.locator('[data-test="finish"]')
        self.error_message = page.locator('[data-test="error"]')
        self.complete_header = page.locator('[data-test="complete-header"]')

    def fill_customer_information(
        self,
        first_name: str,
        last_name: str,
        postal_code: str,
    ) -> None:
        self.first_name.fill(first_name)
        self.last_name.fill(last_name)
        self.postal_code.fill(postal_code)
        self.continue_button.click()

    def continue_without_information(self) -> None:
        self.continue_button.click()

    def finish(self) -> None:
        expect(self.finish_button).to_be_visible()
        self.finish_button.click()

    def order_is_complete(self) -> bool:
        expect(self.complete_header).to_have_text("Thank you for your order!")
        return self.complete_header.is_visible()
