"""
Manual test to verify mouse interaction on app.py canvas.
Run this AFTER starting: uv run uvicorn app:fastapi_app --host 127.0.0.1 --port 8000
"""
import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Enable console logging
        page.on("console", lambda msg: print(f"BROWSER CONSOLE [{msg.type}]: {msg.text}"))
        page.on("pageerror", lambda err: print(f"BROWSER ERROR: {err}"))

        print("=" * 60)
        print("Navigating to http://127.0.0.1:8000")
        print("=" * 60)
        await page.goto("http://127.0.0.1:8000")
        await page.wait_for_timeout(2000)

        # Get canvas element
        print("\n=== Getting Canvas Element ===")
        canvas = page.locator('[style*="background-image"]').first
        count = await canvas.count()
        print(f"Canvas elements found: {count}")

        if count == 0:
            print("ERROR: Canvas element not found!")
            await browser.close()
            return

        box = await canvas.bounding_box()
        print(f"Canvas bounding box: {box}")

        # Try mouse drag operation
        print("\n=== Attempting Mouse Drag ===")
        start_x = box["x"] + 100
        start_y = box["y"] + 100
        end_x = box["x"] + 200
        end_y = box["y"] + 200

        print(f"Start: ({start_x}, {start_y})")
        print(f"End: ({end_x}, {end_y})")

        await page.mouse.move(start_x, start_y)
        await page.mouse.down()
        await page.wait_for_timeout(100)
        await page.mouse.move(end_x, end_y)
        await page.wait_for_timeout(100)
        await page.mouse.up()
        await page.wait_for_timeout(1000)

        # Check if input form appeared
        print("\n=== Checking for Input Form ===")
        select_count = await page.locator("select").count()
        print(f"Total select elements: {select_count}")

        if select_count > 1:
            print("✓ Input form appeared (select count > 1)")
            # Try to select a label
            print("\n=== Selecting Label ===")
            label_select = page.locator("select[autofocus]")
            if await label_select.count() > 0:
                print("Found autofocus select element")
                await label_select.select_option(index=1)
                await page.wait_for_timeout(500)
            else:
                print("WARNING: No autofocus select found")
        else:
            print("✗ Input form did not appear")

        # Check entries
        print("\n=== Checking Entries ===")
        entries_view = page.locator("pre")
        entries_text = await entries_view.text_content()
        print(f"Entries: {entries_text[:200]}")

        # Check for delete button
        print("\n=== Checking for Delete Button ===")
        delete_button = page.locator('button:has-text("x")')
        delete_count = await delete_button.count()
        print(f"Delete buttons found: {delete_count}")

        # Get page content
        print("\n=== Page Content (first 2000 chars) ===")
        content = await page.content()
        print(content[:2000])

        # Take screenshot
        print("\n=== Taking Screenshot ===")
        await page.screenshot(path="/home/user/reactpy_bbox_annotator_sandbox/app_interaction_screenshot.png")
        print("Screenshot saved to app_interaction_screenshot.png")

        await browser.close()
        print("\n" + "=" * 60)
        print("Test completed!")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
