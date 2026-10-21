"""Login behavior tests for the public SauceDemo website."""

from __future__ import annotations

import pytest
from playwright.sync_api import expect

from ui_tests.pages.inventory_page import InventoryPage
from ui_tests.pages.login_page import LoginPage


@pytest.mark.ui
@pytest.mark.smoke
def test_login_page_is_available(page):
    login_page = LoginPage(page)
    login_page.open()

    assert page.title() == "Swag Labs"
    assert login_page.is_loaded()
    expect(login_page.login_button).to_have_text("Login")


@pytest.mark.ui
@pytest.mark.smoke
def test_standard_user_can_log_in(page):
    login_page = LoginPage(page)
    login_page.open()
    login_page.login("standard_user", "secret_sauce")

    inventory_page = InventoryPage(page)
    inventory_page.wait_until_loaded()
    assert page.url.endswith(InventoryPage.URL_FRAGMENT)


@pytest.mark.ui
def test_wrong_password_shows_error(page):
    login_page = LoginPage(page)
    login_page.open()
    login_page.login("standard_user", "wrong-password")

    expect(login_page.error_message).to_contain_text(
        "Username and password do not match"
    )


@pytest.mark.ui
def test_locked_user_is_rejected(page):
    login_page = LoginPage(page)
    login_page.open()
    login_page.login("locked_out_user", "secret_sauce")

    expect(login_page.error_message).to_contain_text(
        "Sorry, this user has been locked out"
    )


@pytest.mark.ui
def test_user_can_log_out(page):
    login_page = LoginPage(page)
    login_page.open()
    login_page.login("standard_user", "secret_sauce")

    inventory_page = InventoryPage(page)
    inventory_page.wait_until_loaded()
    inventory_page.logout()

    expect(page).to_have_url(LoginPage.URL)
    assert login_page.is_loaded()
