"""
Toy problem to understand ReactPy async patterns and html element syntax.
This helps us fix the issues in app.py.
"""

import asyncio

import pytest
from reactpy import component, html, use_effect, use_state
from reactpy.testing import BackendFixture, DisplayFixture


@pytest.fixture
async def display():
    async with BackendFixture() as backend:
        async with DisplayFixture(backend=backend) as display:
            yield display


@pytest.mark.asyncio
async def test_use_effect_with_async(display: DisplayFixture):
    """Test async operations in use_effect."""

    @component
    def AsyncComponent():
        data, set_data = use_state("loading")

        @use_effect
        async def load_data():
            await asyncio.sleep(0.1)
            set_data("loaded")

        return html.div(data)

    await display.show(AsyncComponent)
    await display.page.wait_for_selector("text=loaded")
    content = await display.page.text_content("#app")
    assert content is not None and "loaded" in content


@pytest.mark.asyncio
async def test_button_with_event_and_style(display: DisplayFixture):
    """Test html.button with event handler and style props."""

    @component
    def ButtonComponent():
        count, set_count = use_state(0)

        def handle_click(event):
            set_count(count + 1)

        return html.div(
            html.button(
                {
                    "on_click": handle_click,
                    "style": {"cursor": "pointer", "width": "120px"},
                },
                f"Clicked {count} times",
            )
        )

    await display.show(ButtonComponent)
    button = await display.page.wait_for_selector("button")
    text = await button.text_content()
    assert text is not None and "Clicked 0 times" in text
    cursor = await button.evaluate("el => el.style.cursor")
    width = await button.evaluate("el => el.style.width")
    assert cursor == "pointer"
    assert width == "120px"


@pytest.mark.asyncio
async def test_multiple_html_elements(display: DisplayFixture):
    """Test various html elements with props."""

    @component
    def MultiElementComponent():
        text, set_text = use_state("")

        def on_input(event):
            set_text(event["target"]["value"])

        def on_submit(event):
            set_text(f"Submitted: {text}")

        return html.div(
            html.h2("Test Title"),
            html.input(
                {
                    "type": "text",
                    "value": text,
                    "on_change": on_input,
                    "placeholder": "Enter text",
                }
            ),
            html.button({"on_click": on_submit}, "Submit"),
            html.p(text if text else "No text yet"),
        )

    await display.show(MultiElementComponent)
    await display.page.wait_for_selector("h2:has-text('Test Title')")
    input_elem = await display.page.wait_for_selector("input[type='text']")
    placeholder = await input_elem.get_attribute("placeholder")
    assert placeholder == "Enter text"
    await display.page.wait_for_selector("button:has-text('Submit')")
    paragraph = await display.page.wait_for_selector("p")
    para_text = await paragraph.text_content()
    assert para_text is not None and "No text yet" in para_text


@pytest.mark.asyncio
async def test_conditional_rendering(display: DisplayFixture):
    """Test conditional rendering patterns."""

    @component
    def ConditionalComponent():
        show, set_show = use_state(True)

        def toggle(event):
            set_show(not show)

        if show:
            content = html.p("Visible content")
        else:
            content = html.p("Hidden state")

        return html.div(html.button({"on_click": toggle}, "Toggle"), content)

    await display.show(ConditionalComponent)
    await display.page.wait_for_selector("p:has-text('Visible content')")


@pytest.mark.asyncio
async def test_nested_components_with_state(display: DisplayFixture):
    """Test nested components with state management."""

    @component
    def ChildComponent(value, on_change):
        return html.button(
            {"on_click": lambda e: on_change(value + 1)}, f"Value: {value}"
        )

    @component
    def ParentComponent():
        count, set_count = use_state(0)

        return html.div(html.h3("Parent"), ChildComponent(count, set_count))

    await display.show(ParentComponent)
    button = await display.page.wait_for_selector("button")
    text = await button.text_content()
    assert text is not None and "Value: 0" in text


@pytest.mark.asyncio
async def test_use_effect_with_dependencies(display: DisplayFixture):
    """Test use_effect with dependencies array."""

    @component
    def EffectComponent():
        url, set_url = use_state("url1")
        meta, set_meta = use_state(None)

        @use_effect(dependencies=[url])
        async def load_meta():
            await asyncio.sleep(0.05)
            set_meta(f"Meta for {url}")

        return html.div(
            html.button({"on_click": lambda e: set_url("url2")}, "Change URL"),
            html.p(meta if meta else "Loading..."),
        )

    await display.show(EffectComponent)
    await display.page.wait_for_selector("p:has-text('Meta for url1')")


@pytest.mark.asyncio
async def test_async_image_meta_pattern(display: DisplayFixture):
    """Test the pattern we need for async image metadata loading."""

    @component
    def ImageMetaLoader():
        url, set_url = use_state("https://example.com/image1.jpg")
        meta, set_meta = use_state({"width": 0, "height": 0})
        loading, set_loading = use_state(True)

        @use_effect(dependencies=[url])
        async def fetch_meta():
            set_loading(True)
            try:
                await asyncio.sleep(0.05)
                new_meta = {"width": 800, "height": 600}
                set_meta(new_meta)
            finally:
                set_loading(False)

        if loading:
            content = html.p("Loading image metadata...")
        else:
            content = html.div(
                html.p(f"Width: {meta['width']}"), html.p(f"Height: {meta['height']}")
            )

        return html.div(
            html.input(
                {
                    "type": "text",
                    "value": url,
                    "on_change": lambda e: set_url(e["target"]["value"]),
                }
            ),
            content,
        )

    await display.show(ImageMetaLoader)
    await display.page.wait_for_selector("p:has-text('Width: 800')")
    await display.page.wait_for_selector("p:has-text('Height: 600')")
