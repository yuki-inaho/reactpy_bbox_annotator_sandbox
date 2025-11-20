"""
Toy app to test ReactPy 1.1.0 patterns in isolation.
Run with: uv run uvicorn toy_app:app --host 127.0.0.1 --port 8001
"""
import asyncio
from dataclasses import dataclass
from fastapi import FastAPI
from reactpy import component, html, use_state, use_effect
from reactpy.backend.fastapi import configure


app = FastAPI()


@dataclass
class ImageMeta:
    width: int
    height: int
    url: str


@component
def TestAsyncEffect():
    """Test async use_effect pattern."""
    data, set_data = use_state("loading")

    @use_effect
    async def load_data():
        await asyncio.sleep(0.5)
        set_data("Data loaded!")

    return html.div(
        html.h3("Test 1: Async use_effect"),
        html.p(data)
    )


@component
def TestButtonSyntax():
    """Test html.button with event handler and style."""
    count, set_count = use_state(0)

    def handle_click(event):
        set_count(count + 1)

    return html.div(
        html.h3("Test 2: Button with event and style"),
        html.button(
            {
                "on_click": handle_click,
                "style": {"cursor": "pointer", "width": "200px", "padding": "10px"}
            },
            f"Clicked {count} times"
        )
    )


@component
def TestImageMetaPattern():
    """Test the pattern for async image metadata loading."""
    url, set_url = use_state("https://example.com/image1.jpg")
    meta, set_meta = use_state(None)
    loading, set_loading = use_state(True)
    error, set_error = use_state("")

    @use_effect(dependencies=[url])
    async def fetch_meta():
        set_loading(True)
        set_error("")
        try:
            # Simulate async fetch
            await asyncio.sleep(0.3)
            # In real code, this would fetch actual image metadata
            new_meta = ImageMeta(width=800, height=600, url=url)
            set_meta(new_meta)
        except Exception as e:
            set_error(f"Error: {e}")
        finally:
            set_loading(False)

    def handle_url_change(event):
        set_url(event["target"]["value"])

    def handle_load_click(event):
        # Force re-fetch by updating URL (even if same)
        set_loading(True)

    if loading:
        content = html.p({"style": {"color": "gray"}}, "Loading image metadata...")
    elif error:
        content = html.p({"style": {"color": "red"}}, error)
    elif meta:
        content = html.div(
            html.p(f"URL: {meta.url}"),
            html.p(f"Width: {meta.width}px"),
            html.p(f"Height: {meta.height}px")
        )
    else:
        content = html.p("No metadata")

    return html.div(
        html.h3("Test 3: Image metadata pattern"),
        html.div(
            html.input({
                "type": "text",
                "value": url,
                "on_change": handle_url_change,
                "style": {"width": "400px", "padding": "5px"}
            }),
            html.button(
                {
                    "on_click": handle_load_click,
                    "style": {"margin_left": "10px", "padding": "5px 15px"}
                },
                "Reload"
            )
        ),
        content
    )


@component
def TestMultipleElements():
    """Test various html elements with proper syntax."""
    text, set_text = use_state("")
    selected, set_selected = use_state("option1")

    def on_input_change(event):
        set_text(event["target"]["value"])

    def on_select_change(event):
        set_selected(event["target"]["value"])

    def on_submit(event):
        set_text(f"Submitted: {text}")

    return html.div(
        html.h3("Test 4: Multiple element types"),
        html.div(
            html.label("Text input: "),
            html.input({
                "type": "text",
                "value": text,
                "on_change": on_input_change,
                "placeholder": "Enter text",
                "style": {"padding": "5px"}
            })
        ),
        html.div(
            html.label("Select: "),
            html.select(
                {
                    "value": selected,
                    "on_change": on_select_change,
                    "style": {"padding": "5px"}
                },
                html.option({"value": "option1"}, "Option 1"),
                html.option({"value": "option2"}, "Option 2"),
                html.option({"value": "option3"}, "Option 3")
            )
        ),
        html.button(
            {"on_click": on_submit, "style": {"padding": "5px 15px"}},
            "Submit"
        ),
        html.p(f"Text: {text}"),
        html.p(f"Selected: {selected}")
    )


@component
def TestConditionalRendering():
    """Test conditional rendering and component composition."""
    status, set_status = use_state("free")
    show_details, set_show_details = use_state(False)

    def toggle_details(event):
        set_show_details(not show_details)

    def change_status(new_status):
        return lambda event: set_status(new_status)

    # Conditional content
    if show_details:
        details = html.div(
            {"style": {"background_color": "#f0f0f0", "padding": "10px", "margin": "10px 0"}},
            html.p(f"Current status: {status}"),
            html.p("This is additional detail content")
        )
    else:
        details = None

    return html.div(
        html.h3("Test 5: Conditional rendering"),
        html.div(
            html.button({"on_click": change_status("free")}, "Free"),
            html.button({"on_click": change_status("busy"), "style": {"margin_left": "5px"}}, "Busy"),
            html.button({"on_click": change_status("waiting"), "style": {"margin_left": "5px"}}, "Waiting")
        ),
        html.p(f"Status: {status}"),
        html.button(
            {"on_click": toggle_details},
            f"{'Hide' if show_details else 'Show'} Details"
        ),
        details if details else html.div()
    )


@component
def ToyApp():
    """Main toy app component."""
    return html.div(
        {"style": {"padding": "20px", "font_family": "sans-serif"}},
        html.h1("ReactPy 1.1.0 Pattern Tests"),
        html.hr(),
        TestAsyncEffect(),
        html.hr(),
        TestButtonSyntax(),
        html.hr(),
        TestImageMetaPattern(),
        html.hr(),
        TestMultipleElements(),
        html.hr(),
        TestConditionalRendering()
    )


configure(app, ToyApp)
