"""Page object for the SauceDemo login page."""

from __future__ import annotations

from playwright.sync_api import Page, expect


class LoginPage:
    URL = "https://www.saucedemo.com/"

    def __init__(self, page: Page) -> None:
        self.page = page
        self.username = page.locator('[data-test="username"]')
        self.password = page.locator('[data-test="password"]')
        self.login_button = page.locator('[data-test="login-button"]')
        self.error_message = page.locator('[data-test="error"]')

    def open(self) -> None:
        self.page.goto(self.URL, wait_until="domcontentloaded")

    def is_loaded(self) -> bool:
        expect(self.login_button).to_be_visible()
        return self.login_button.is_visible()

    def login(self, username: str, password: str) -> None:
        self.username.fill(username)
        self.password.fill(password)
        self.login_button.click()
