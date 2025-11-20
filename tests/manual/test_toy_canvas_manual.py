"""
Manual test for toy_canvas_test.py to debug canvas element detection.
Run this AFTER starting: uv run uvicorn toy_canvas_test:fastapi_app --host 127.0.0.1 --port 8002
"""

import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Enable console logging
        page.on(
            "console", lambda msg: print(f"BROWSER CONSOLE [{msg.type}]: {msg.text}")
        )
        page.on("pageerror", lambda err: print(f"BROWSER ERROR: {err}"))

        # Navigate to toy app
        print("=" * 60)
        print("Navigating to http://127.0.0.1:8002")
        print("=" * 60)
        await page.goto("http://127.0.0.1:8002")
        await page.wait_for_timeout(2000)

        # Check page title
        print("\n=== Page Title ===")
        title = await page.title()
        print(f"Title: {title}")

        # Check h1
        print("\n=== H1 Element ===")
        try:
            h1 = await page.text_content("h1", timeout=5000)
            print(f"H1 text: {h1}")
        except Exception as e:
            print(f"Error finding h1: {e}")

        # Wait for image to load
        print("\n=== Waiting for image load ===")
        await page.wait_for_timeout(3000)

        # Check for canvas element by data-testid
        print("\n=== Canvas Element (by data-testid) ===")
        canvas_testid = page.locator('[data-testid="canvas-element"]')
        count_testid = await canvas_testid.count()
        print(f"Canvas elements found by testid: {count_testid}")

        if count_testid > 0:
            style = await canvas_testid.first.get_attribute("style")
            print(f"Canvas style: {style[:300]}...")

        # Check for canvas element by backgroundImage (camelCase)
        print("\n=== Canvas Element (by backgroundImage camelCase) ===")
        canvas_camel = page.locator('[style*="backgroundImage"]')
        count_camel = await canvas_camel.count()
        print(f"Canvas elements found by backgroundImage (camelCase): {count_camel}")

        # Check for canvas element by background-image (kebab-case)
        print("\n=== Canvas Element (by background-image kebab-case) ===")
        canvas_kebab = page.locator('[style*="background-image"]')
        count_kebab = await canvas_kebab.count()
        print(f"Canvas elements found by background-image (kebab-case): {count_kebab}")

        if count_kebab > 0:
            style = await canvas_kebab.first.get_attribute("style")
            print(f"Canvas style: {style[:300]}...")

        # Get all divs
        print("\n=== All Divs ===")
        all_divs = page.locator("div")
        div_count = await all_divs.count()
        print(f"Total divs: {div_count}")

        # Check for divs with position: relative
        print("\n=== Divs with position: relative ===")
        relative_divs = page.locator('div[style*="position: relative"]')
        count_relative = await relative_divs.count()
        print(f"Divs with 'position: relative': {count_relative}")

        if count_relative > 0:
            for i in range(min(count_relative, 3)):
                style = await relative_divs.nth(i).get_attribute("style")
                print(f"  Div {i} style: {style[:200]}...")

        # Get page content
        print("\n=== Page Content (first 3000 chars) ===")
        content = await page.content()
        print(content[:3000])

        # Take screenshot
        print("\n=== Taking Screenshot ===")
        await page.screenshot(
            path="/home/user/reactpy_bbox_annotator_sandbox/toy_canvas_screenshot.png"
        )
        print("Screenshot saved to toy_canvas_screenshot.png")

        await browser.close()
        print("\n" + "=" * 60)
        print("Test completed!")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
