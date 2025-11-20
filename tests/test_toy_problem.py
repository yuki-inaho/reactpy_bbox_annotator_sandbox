"""
Toy problem to understand ReactPy 1.1.0 async patterns and html element syntax.
This helps us fix the issues in app.py.
"""
import asyncio
import pytest
from reactpy import component, html, use_state, use_effect
from reactpy.testing import DisplayFixture, BackendFixture
from reactpy.core.events import event


@pytest.mark.asyncio
async def test_use_effect_with_async():
    """Test async operations in use_effect."""

    @component
    def AsyncComponent():
        data, set_data = use_state("loading")

        @use_effect
        async def load_data():
            await asyncio.sleep(0.1)
            set_data("loaded")

        return html.div(data)

    async with DisplayFixture(AsyncComponent) as display:
        await display.poll(lambda: display.root.children[0] == "loaded", timeout=1.0)
        assert display.root.children[0] == "loaded"


@pytest.mark.asyncio
async def test_button_with_event_and_style():
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
                    "style": {"cursor": "pointer", "width": "120px"}
                },
                f"Clicked {count} times"
            )
        )

    async with DisplayFixture(ButtonComponent) as display:
        await display.poll(lambda: "Clicked 0 times" in str(display.root), timeout=1.0)

        # Find the button element in VDOM
        button = display.root.children[0]
        assert button["tagName"] == "button"
        assert button["attributes"]["style"]["cursor"] == "pointer"


@pytest.mark.asyncio
async def test_multiple_html_elements():
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
            html.input({
                "type": "text",
                "value": text,
                "on_change": on_input,
                "placeholder": "Enter text"
            }),
            html.button(
                {"on_click": on_submit},
                "Submit"
            ),
            html.p(text if text else "No text yet")
        )

    async with DisplayFixture(MultiElementComponent) as display:
        await display.poll(lambda: display.root is not None, timeout=1.0)

        # Verify structure
        assert display.root["tagName"] == "div"
        assert len(display.root["children"]) == 4

        # Verify h2
        h2 = display.root["children"][0]
        assert h2["tagName"] == "h2"
        assert h2["children"][0] == "Test Title"

        # Verify input
        input_elem = display.root["children"][1]
        assert input_elem["tagName"] == "input"
        assert input_elem["attributes"]["type"] == "text"

        # Verify button
        button = display.root["children"][2]
        assert button["tagName"] == "button"
        assert button["children"][0] == "Submit"


@pytest.mark.asyncio
async def test_conditional_rendering():
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

        return html.div(
            html.button({"on_click": toggle}, "Toggle"),
            content
        )

    async with DisplayFixture(ConditionalComponent) as display:
        await display.poll(lambda: display.root is not None, timeout=1.0)

        # Initial state
        p_elem = display.root["children"][1]
        assert p_elem["children"][0] == "Visible content"


@pytest.mark.asyncio
async def test_nested_components_with_state():
    """Test nested components with state management."""

    @component
    def ChildComponent(value, on_change):
        return html.button(
            {"on_click": lambda e: on_change(value + 1)},
            f"Value: {value}"
        )

    @component
    def ParentComponent():
        count, set_count = use_state(0)

        return html.div(
            html.h3("Parent"),
            ChildComponent(count, set_count)
        )

    async with DisplayFixture(ParentComponent) as display:
        await display.poll(lambda: display.root is not None, timeout=1.0)

        # Verify child button
        button = display.root["children"][1]
        assert button["tagName"] == "button"
        assert "Value: 0" in str(button["children"])


@pytest.mark.asyncio
async def test_use_effect_with_dependencies():
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
            html.p(meta if meta else "Loading...")
        )

    async with DisplayFixture(EffectComponent) as display:
        await display.poll(
            lambda: "Meta for url1" in str(display.root),
            timeout=1.0
        )

        p_elem = display.root["children"][1]
        assert "Meta for url1" in str(p_elem["children"])


@pytest.mark.asyncio
async def test_async_image_meta_pattern():
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
                # Simulate async fetch
                await asyncio.sleep(0.05)
                # In real code, this would fetch actual image metadata
                new_meta = {"width": 800, "height": 600}
                set_meta(new_meta)
            finally:
                set_loading(False)

        if loading:
            content = html.p("Loading image metadata...")
        else:
            content = html.div(
                html.p(f"Width: {meta['width']}"),
                html.p(f"Height: {meta['height']}")
            )

        return html.div(
            html.input({
                "type": "text",
                "value": url,
                "on_change": lambda e: set_url(e["target"]["value"])
            }),
            content
        )

    async with DisplayFixture(ImageMetaLoader) as display:
        await display.poll(
            lambda: "Width: 800" in str(display.root),
            timeout=1.0
        )

        # Verify metadata was loaded
        div_content = display.root["children"][1]
        assert "Width: 800" in str(div_content)
        assert "Height: 600" in str(div_content)
