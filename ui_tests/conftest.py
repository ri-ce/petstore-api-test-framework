"""Browser fixtures and failure screenshots for SauceDemo tests."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Iterator

import pytest
from playwright.sync_api import Browser, Page, sync_playwright


SCREENSHOT_DIR = Path(__file__).resolve().parents[1] / "reports" / "screenshots"


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture(scope="session")
def browser() -> Iterator[Browser]:
    with sync_playwright() as playwright:
        channel = os.getenv("PLAYWRIGHT_BROWSER_CHANNEL")
        if channel:
            browser_instance = playwright.chromium.launch(
                headless=True,
                channel=channel,
            )
        else:
            try:
                browser_instance = playwright.chromium.launch(headless=True)
            except Exception:
                browser_instance = playwright.chromium.launch(
                    headless=True,
                    channel="chrome",
                )
        yield browser_instance
        browser_instance.close()


@pytest.fixture
def page(browser: Browser, request) -> Iterator[Page]:
    context = browser.new_context(
        viewport={"width": 1440, "height": 1000},
        locale="en-US",
    )
    page_instance = context.new_page()
    page_instance.set_default_timeout(15_000)
    page_instance.set_default_navigation_timeout(30_000)
    yield page_instance

    report = getattr(request.node, "rep_call", None)
    if report is not None and report.failed:
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        safe_name = re.sub(
            r"[^A-Za-z0-9_.-]+",
            "_",
            request.node.nodeid,
        )
        page_instance.screenshot(
            path=SCREENSHOT_DIR / f"{safe_name}.png",
            full_page=True,
        )
    context.close()
