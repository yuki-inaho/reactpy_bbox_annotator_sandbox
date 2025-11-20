"""
pytest configuration and fixtures for E2E tests.
"""

import multiprocessing
import time
from pathlib import Path
import pytest
import uvicorn
from playwright.async_api import async_playwright


def run_server():
    """Run FastAPI server in a separate process."""
    import sys

    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root))
    from app import fastapi_app

    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000, log_level="error")


@pytest.fixture(scope="session")
def server():
    """Start FastAPI server for the test session."""
    proc = multiprocessing.Process(target=run_server, daemon=True)
    proc.start()
    time.sleep(2)  # サーバー起動を待つ
    yield
    proc.terminate()
    proc.join(timeout=5)


@pytest.fixture(scope="function")
async def browser():
    """Provide a Playwright browser instance."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        yield browser
        await browser.close()


@pytest.fixture(scope="function")
async def page(browser):
    """Provide a Playwright page instance."""
    page = await browser.new_page()
    yield page
    await page.close()
