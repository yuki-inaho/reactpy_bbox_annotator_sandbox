"""
Manual test to verify ReactPy patterns work correctly.
"""

import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Navigate to toy app
        await page.goto("http://127.0.0.1:8001")
        await page.wait_for_timeout(2000)

        # Test 1: Check if async effect loaded
        print("Test 1: Async use_effect")
        text = await page.text_content("body")
        if "Data loaded!" in text:
            print("  ✓ Async effect works")
        else:
            print(f"  ✗ Async effect failed. Text: {text[:200]}")

        # Test 2: Check button
        print("\nTest 2: Button with event and style")
        button = page.locator('button:has-text("Clicked 0 times")')
        if await button.count() > 0:
            print("  ✓ Button rendered")
            await button.click()
            await page.wait_for_timeout(500)
            if await page.locator('button:has-text("Clicked 1 times")').count() > 0:
                print("  ✓ Button click event works")
            else:
                print("  ✗ Button click event failed")
        else:
            print("  ✗ Button not found")

        # Test 3: Check image meta pattern
        print("\nTest 3: Image metadata pattern")
        await page.wait_for_timeout(500)
        if "Width: 800px" in await page.text_content("body"):
            print("  ✓ Async image metadata loading works")
        else:
            print("  ✗ Image metadata loading failed")

        # Test 4: Check input
        print("\nTest 4: Input element")
        input_elem = page.locator('input[type="text"]').first
        if await input_elem.count() > 0:
            print("  ✓ Input element rendered")
            await input_elem.fill("test input")
            await page.wait_for_timeout(500)
            if "test input" in await page.text_content("body"):
                print("  ✓ Input change event works")
            else:
                print("  ✗ Input change event failed")
        else:
            print("  ✗ Input not found")

        # Test 5: Check select
        print("\nTest 5: Select element")
        select_elem = page.locator("select").first
        if await select_elem.count() > 0:
            print("  ✓ Select element rendered")
            await select_elem.select_option("option2")
            await page.wait_for_timeout(500)
            if "Selected: option2" in await page.text_content("body"):
                print("  ✓ Select change event works")
            else:
                print("  ✗ Select change event failed")
        else:
            print("  ✗ Select not found")

        # Test 6: Check conditional rendering
        print("\nTest 6: Conditional rendering")
        toggle_button = page.locator('button:has-text("Show Details")')
        if await toggle_button.count() > 0:
            print("  ✓ Conditional button rendered")
            await toggle_button.click()
            await page.wait_for_timeout(500)
            if "This is additional detail content" in await page.text_content("body"):
                print("  ✓ Conditional rendering works")
            else:
                print("  ✗ Conditional rendering failed")
        else:
            print("  ✗ Conditional button not found")

        print("\n" + "=" * 50)
        print("All pattern tests completed!")
        print("=" * 50)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
