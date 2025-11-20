"""
E2E tests for BBox Annotator using Playwright.
TDD approach: Write tests first, then implement functionality.
"""
import asyncio
import pytest
from playwright.async_api import async_playwright, Page


@pytest.mark.asyncio
async def test_bbox_annotator_basic_flow(server, page):
    """
    Test basic annotation flow:
    1. ページにアクセス
    2. 初期状態を確認
    """
    # ページにアクセス
    await page.goto("http://127.0.0.1:8000")
    await page.wait_for_timeout(1000)

    # タイトルを確認
    title = await page.text_content("h2")
    assert "ReactPy Bounding Box Annotator" in title

    # 画像が表示されることを確認（デフォルト画像）
    # Canvas要素が存在することを確認
    canvas = page.locator('[style*="backgroundImage"]').first
    await canvas.wait_for()
    assert await canvas.count() > 0


@pytest.mark.asyncio
async def test_bbox_annotation_select_mode(server, page):
    """
    Test annotation with select mode:
    - ドラッグでボックスを作成
    - セレクトボックスからラベルを選択
    - エントリが正しく追加されることを確認
    """
    await page.goto("http://127.0.0.1:8000")
    await page.wait_for_timeout(1000)

    # Canvas要素を取得
    canvas = page.locator('[style*="backgroundImage"]').first
    box = await canvas.bounding_box()
    assert box is not None

    # ドラッグでボックスを作成（左上から右下へ）
    start_x = box["x"] + 100
    start_y = box["y"] + 100
    end_x = box["x"] + 200
    end_y = box["y"] + 200

    await page.mouse.move(start_x, start_y)
    await page.mouse.down()
    await page.mouse.move(end_x, end_y)
    await page.mouse.up()
    await page.wait_for_timeout(500)

    # セレクトボックスが表示されることを確認
    select = page.locator("select")
    await select.wait_for()

    # ラベルを選択（最初のオプション）
    await select.select_option(index=1)
    await page.wait_for_timeout(500)

    # エントリが追加されたことを確認（JSONビュー）
    entries_view = page.locator("pre")
    text = await entries_view.text_content()
    assert "label" in text
    assert "Mama cow" in text or "Baby cow" in text


@pytest.mark.asyncio
async def test_bbox_annotation_text_mode(server, page):
    """
    Test annotation with text mode:
    - input method を text に変更
    - ドラッグでボックスを作成
    - テキスト入力でラベルを追加
    - エントリが正しく追加されることを確認
    """
    await page.goto("http://127.0.0.1:8000")
    await page.wait_for_timeout(1000)

    # Input method を text に変更
    input_method_select = page.locator('select').nth(1)  # 2番目のselectがinput method
    await input_method_select.select_option("text")
    await page.wait_for_timeout(500)

    # ボックスを作成
    canvas = page.locator('[style*="backgroundImage"]').first
    box = await canvas.bounding_box()
    assert box is not None

    start_x = box["x"] + 100
    start_y = box["y"] + 100
    end_x = box["x"] + 200
    end_y = box["y"] + 200

    await page.mouse.move(start_x, start_y)
    await page.mouse.down()
    await page.mouse.move(end_x, end_y)
    await page.mouse.up()
    await page.wait_for_timeout(500)

    # テキスト入力が表示されることを確認
    text_input = page.locator('input[type="text"]')
    await text_input.wait_for()

    # ラベルを入力
    await text_input.fill("test label")
    await page.keyboard.press("Enter")
    await page.wait_for_timeout(500)

    # エントリが追加されたことを確認
    entries_view = page.locator("pre")
    text = await entries_view.text_content()
    assert "test label" in text


@pytest.mark.asyncio
async def test_bbox_delete_entry(server, page):
    """
    Test deleting an entry:
    - ボックスを作成してラベルを追加
    - 削除ボタンをクリック
    - エントリが削除されることを確認
    """
    await page.goto("http://127.0.0.1:8000")
    await page.wait_for_timeout(1000)

    # ボックスを作成してラベルを追加
    canvas = page.locator('[style*="backgroundImage"]').first
    box = await canvas.bounding_box()
    assert box is not None

    await page.mouse.move(box["x"] + 100, box["y"] + 100)
    await page.mouse.down()
    await page.mouse.move(box["x"] + 200, box["y"] + 200)
    await page.mouse.up()
    await page.wait_for_timeout(500)

    # ラベルを選択
    select = page.locator("select").first
    await select.select_option(index=1)
    await page.wait_for_timeout(500)

    # 削除ボタンをクリック
    delete_button = page.locator('button:has-text("x")')
    await delete_button.click()
    await page.wait_for_timeout(500)

    # エントリが削除されたことを確認
    entries_view = page.locator("pre")
    text = await entries_view.text_content()
    assert text.strip() == "[]" or '"label"' not in text


@pytest.mark.asyncio
async def test_bbox_reset_entries(server, page):
    """
    Test resetting all entries:
    - 複数のボックスを作成
    - リセットボタンをクリック
    - 全てのエントリがクリアされることを確認
    """
    await page.goto("http://127.0.0.1:8000")
    await page.wait_for_timeout(1000)

    # 2つのボックスを作成
    canvas = page.locator('[style*="backgroundImage"]').first
    box = await canvas.bounding_box()
    assert box is not None

    # 1つ目
    await page.mouse.move(box["x"] + 50, box["y"] + 50)
    await page.mouse.down()
    await page.mouse.move(box["x"] + 150, box["y"] + 150)
    await page.mouse.up()
    await page.wait_for_timeout(500)
    select = page.locator("select").first
    await select.select_option(index=1)
    await page.wait_for_timeout(500)

    # 2つ目
    await page.mouse.move(box["x"] + 250, box["y"] + 250)
    await page.mouse.down()
    await page.mouse.move(box["x"] + 350, box["y"] + 350)
    await page.mouse.up()
    await page.wait_for_timeout(500)
    await select.select_option(index=1)
    await page.wait_for_timeout(500)

    # リセットボタンをクリック
    reset_button = page.locator('button:has-text("Reset entries")')
    await reset_button.click()
    await page.wait_for_timeout(500)

    # エントリがクリアされたことを確認
    entries_view = page.locator("pre")
    text = await entries_view.text_content()
    assert text.strip() == "[]"


@pytest.mark.asyncio
async def test_bbox_change_image_url(server, page):
    """
    Test changing image URL:
    - 新しいURLを入力
    - Load imageボタンをクリック
    - 画像が切り替わることを確認
    """
    await page.goto("http://127.0.0.1:8000")
    await page.wait_for_timeout(1000)

    # 新しいURLを入力
    url_input = page.locator('input[type="text"]').first
    new_url = "https://via.placeholder.com/600x400"
    await url_input.fill(new_url)

    # Load imageボタンをクリック
    load_button = page.locator('button:has-text("Load image")')
    await load_button.click()
    await page.wait_for_timeout(2000)  # 画像読み込みを待つ

    # 画像が切り替わったことを確認
    canvas = page.locator('[style*="backgroundImage"]').first
    style = await canvas.get_attribute("style")
    assert new_url in style or "via.placeholder.com" in style


@pytest.mark.asyncio
async def test_bbox_cancel_input(server, page):
    """
    Test canceling label input:
    - ドラッグでボックスを作成
    - Cancelボタンをクリック
    - 入力がキャンセルされることを確認
    """
    await page.goto("http://127.0.0.1:8000")
    await page.wait_for_timeout(1000)

    # ボックスを作成
    canvas = page.locator('[style*="backgroundImage"]').first
    box = await canvas.bounding_box()
    assert box is not None

    await page.mouse.move(box["x"] + 100, box["y"] + 100)
    await page.mouse.down()
    await page.mouse.move(box["x"] + 200, box["y"] + 200)
    await page.mouse.up()
    await page.wait_for_timeout(500)

    # Cancelボタンをクリック
    cancel_button = page.locator('button:has-text("Cancel")')
    await cancel_button.click()
    await page.wait_for_timeout(500)

    # 入力がキャンセルされ、エントリが追加されていないことを確認
    entries_view = page.locator("pre")
    text = await entries_view.text_content()
    assert text.strip() == "[]"
