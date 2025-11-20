"""
Manual test for toy_mouse_test.py to debug mouse event handling.
Run this AFTER starting: uv run uvicorn toy_mouse_test:fastapi_app --host 127.0.0.1 --port 8003
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

        print("=" * 60)
        print("Navigating to http://127.0.0.1:8003")
        print("=" * 60)
        await page.goto("http://127.0.0.1:8003")
        await page.wait_for_timeout(2000)

        # Check page title
        print("\n=== Page Title ===")
        title = await page.title()
        print(f"Title: {title}")

        # Get canvas element
        print("\n=== Getting Canvas Element ===")
        canvas = page.locator('[data-testid="mouse-canvas"]')
        count = await canvas.count()
        print(f"Canvas elements found: {count}")

        if count == 0:
            print("ERROR: Canvas element not found!")
            await browser.close()
            return

        box = await canvas.bounding_box()
        print(f"Canvas bounding box: {box}")

        # Check initial status
        print("\n=== Initial Status ===")
        content = await page.content()
        if "Status: waiting" in content:
            print("✓ Initial status: waiting")
        else:
            print("✗ Initial status not 'waiting'")

        # Perform mouse drag operation
        print("\n=== Performing Mouse Drag ===")
        start_x = box["x"] + 100
        start_y = box["y"] + 100
        end_x = box["x"] + 300
        end_y = box["y"] + 250

        print(f"Start: ({start_x}, {start_y})")
        print(f"End: ({end_x}, {end_y})")

        # Mouse down
        await page.mouse.move(start_x, start_y)
        await page.mouse.down()
        await page.wait_for_timeout(200)

        # Check status after mouse down
        content = await page.content()
        if "Status: dragging" in content:
            print("✓ Status changed to 'dragging' after mouse down")
        else:
            print("✗ Status did not change to 'dragging'")
            print(f"  Content snippet: {content[1000:1500]}")

        # Mouse move
        await page.mouse.move(end_x, end_y)
        await page.wait_for_timeout(200)

        # Mouse up
        await page.mouse.up()
        await page.wait_for_timeout(500)

        # Check final status
        print("\n=== Final Status ===")
        content = await page.content()
        if "Status: completed" in content:
            print("✓ Status changed to 'completed' after mouse up")
        else:
            print("✗ Status did not change to 'completed'")

        # Check mouse data
        print("\n=== Mouse Data ===")
        if "Start:" in content and "'x':" in content:
            print("✓ Start position recorded")
        else:
            print("✗ Start position not recorded")

        if "End:" in content and "'x':" in content:
            print("✓ End position recorded")
        else:
            print("✗ End position not recorded")

        # Check event log
        print("\n=== Event Log ===")
        if "MouseDown:" in content:
            print("✓ MouseDown event logged")
        else:
            print("✗ MouseDown event not logged")

        if "MouseMove:" in content:
            print("✓ MouseMove event logged")
        else:
            print("✗ MouseMove event not logged")

        if "MouseUp:" in content:
            print("✓ MouseUp event logged")
        else:
            print("✗ MouseUp event not logged")

        # Check for offsetX/offsetY values
        print("\n=== Checking offsetX/offsetY Values ===")
        import re

        offset_pattern = r"offsetX=(\d+), offsetY=(\d+)"
        matches = re.findall(offset_pattern, content)
        if matches:
            print(f"✓ Found {len(matches)} events with offsetX/offsetY:")
            for i, (x, y) in enumerate(matches[:5]):  # Show first 5
                print(f"  Event {i + 1}: offsetX={x}, offsetY={y}")
        else:
            print("✗ No offsetX/offsetY values found in event log")
            # Check for -1 values (indicating missing offsetX/offsetY)
            if "offsetX=-1" in content:
                print("  WARNING: Found offsetX=-1, indicating missing event property")

        # Get page content for debugging
        print("\n=== Page Content (first 3000 chars) ===")
        print(content[:3000])

        # Take screenshot
        print("\n=== Taking Screenshot ===")
        await page.screenshot(
            path="/home/user/reactpy_bbox_annotator_sandbox/toy_mouse_screenshot.png"
        )
        print("Screenshot saved to toy_mouse_screenshot.png")

        await browser.close()
        print("\n" + "=" * 60)
        print("Test completed!")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
