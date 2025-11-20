"""
Toy problem to debug canvas element detection in E2E tests.
This isolates the issue: Why isn't the canvas element with background-image rendering?
Run with: uv run uvicorn toy_canvas_test:app --host 127.0.0.1 --port 8002
"""
import asyncio
import urllib.request
from dataclasses import dataclass
from io import BytesIO
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from PIL import Image, ImageDraw, ImageFont
from reactpy import component, html, use_effect, use_state
from reactpy.backend.fastapi import configure


MAX_DISPLAY_WIDTH = 900


@dataclass(frozen=True)
class ImageMeta:
    width: int
    height: int


def _fetch_image_meta_sync(url: str) -> ImageMeta:
    """Fetch image metadata from URL synchronously."""
    # Handle relative URLs by converting to absolute
    if url.startswith("/"):
        url = f"http://127.0.0.1:8002{url}"

    with urllib.request.urlopen(url) as response:
        data = response.read()
    with Image.open(BytesIO(data)) as img:
        width, height = img.size
    return ImageMeta(width, height)


async def fetch_image_meta_async(url: str) -> ImageMeta:
    """Fetch image metadata asynchronously."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _fetch_image_meta_sync, url)


@component
def ToyCanvasApp():
    """Minimal canvas test to isolate element detection issue."""
    image_url, set_image_url = use_state("/test_image.png")
    image_meta, set_image_meta = use_state(None)
    display_size, set_display_size = use_state({"width": 0, "height": 0})
    scale, set_scale = use_state(1.0)
    error_message, set_error_message = use_state("")
    loading, set_loading = use_state(True)

    @use_effect(dependencies=[image_url])
    async def load_image_metadata():
        set_loading(True)
        set_error_message("")
        print(f"[ToyCanvas] Loading image: {image_url}")
        try:
            meta = await fetch_image_meta_async(image_url)
            print(f"[ToyCanvas] Image metadata: {meta.width}x{meta.height}")

            factor = min(1.0, MAX_DISPLAY_WIDTH / meta.width) if meta.width else 1.0
            set_scale(factor)
            set_image_meta(meta)
            set_display_size({
                "width": int(meta.width * factor),
                "height": int(meta.height * factor),
            })
            print(f"[ToyCanvas] Display size: {int(meta.width * factor)}x{int(meta.height * factor)}")
        except Exception as exc:
            error_msg = f"Failed to load image: {exc}"
            print(f"[ToyCanvas ERROR] {error_msg}")
            set_error_message(error_msg)
            set_image_meta(None)
            set_display_size({"width": 0, "height": 0})
        finally:
            set_loading(False)

    # Canvas element
    canvas_style = {
        "position": "relative",
        "width": f"{display_size['width']}px",
        "height": f"{display_size['height']}px",
        "backgroundImage": f"url({image_url})" if image_meta else "none",
        "backgroundSize": "contain",
        "backgroundRepeat": "no-repeat",
        "border": "2px solid #333",
        "cursor": "crosshair",
    }

    canvas = html.div(
        {
            "style": canvas_style,
            "data-testid": "canvas-element",
        },
        # Empty content for now
    )

    # Status display
    if loading:
        status_text = "Loading image..."
    elif error_message:
        status_text = f"Error: {error_message}"
    elif image_meta:
        status_text = f"Image loaded: {image_meta.width}x{image_meta.height}px, Display: {display_size['width']}x{display_size['height']}px, Scale: {scale:.3f}"
    else:
        status_text = "No image"

    return html.div(
        {"style": {"padding": "20px", "fontFamily": "sans-serif"}},
        html.h1("Toy Canvas Test"),
        html.p({"style": {"color": "blue" if not error_message else "red"}}, status_text),
        html.div(
            {"style": {"marginTop": "20px"}},
            canvas
        ),
        html.div(
            {"style": {"marginTop": "20px"}},
            html.h3("Debug Info:"),
            html.pre(
                f"image_url: {image_url}\n"
                f"image_meta: {image_meta}\n"
                f"display_size: {display_size}\n"
                f"scale: {scale}\n"
                f"loading: {loading}\n"
                f"error_message: {error_message}"
            )
        )
    )


fastapi_app = FastAPI()


@fastapi_app.get("/test_image.png")
async def get_test_image():
    """Generate a test image."""
    img = Image.new('RGB', (400, 300), color=(100, 150, 200))
    draw = ImageDraw.Draw(img)

    # Draw a simple pattern
    draw.rectangle([50, 50, 150, 150], fill=(255, 100, 100), outline=(255, 255, 255), width=3)
    draw.ellipse([200, 100, 350, 250], fill=(100, 255, 100), outline=(255, 255, 255), width=3)

    # Add text
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
    except:
        font = ImageFont.load_default()
    draw.text((100, 20), "Test Image", fill=(255, 255, 255), font=font)

    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")


configure(fastapi_app, ToyCanvasApp)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("toy_canvas_test:fastapi_app", host="0.0.0.0", port=8002, reload=True)
