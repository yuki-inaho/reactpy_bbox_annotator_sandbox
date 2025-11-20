"""
Manual test to debug app.py rendering issues.
"""

import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Enable console logging
        page.on("console", lambda msg: print(f"CONSOLE: {msg.type}: {msg.text}"))
        page.on("pageerror", lambda err: print(f"PAGE ERROR: {err}"))

        # Navigate to app
        print("Navigating to http://127.0.0.1:8000")
        await page.goto("http://127.0.0.1:8000")
        await page.wait_for_timeout(3000)

        # Check page title
        print("\n=== Page Title ===")
        title = await page.title()
        print(f"Title: {title}")

        # Check h2
        print("\n=== H2 Element ===")
        try:
            h2 = await page.text_content("h2", timeout=5000)
            print(f"H2 text: {h2}")
        except Exception as e:
            print(f"Error finding h2: {e}")

        # Check for canvas element
        print("\n=== Canvas Element ===")
        canvas = page.locator('[style*="backgroundImage"]')
        count = await canvas.count()
        print(f"Canvas elements found: {count}")

        if count > 0:
            style = await canvas.first.get_attribute("style")
            print(f"Canvas style: {style[:200]}...")
        else:
            print("No canvas element found!")

        # Get full page content
        print("\n=== Page Content (first 2000 chars) ===")
        content = await page.content()
        print(content[:2000])

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
