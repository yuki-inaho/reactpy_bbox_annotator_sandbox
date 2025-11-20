import asyncio
import json
import uuid
import urllib.request
from dataclasses import dataclass
from functools import lru_cache
from io import BytesIO
from typing import Dict, List, Optional

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from PIL import Image, ImageDraw, ImageFont
from reactpy import component, html, use_effect, use_state
from reactpy.backend.fastapi import configure
from reactpy.core.events import event


MAX_DISPLAY_WIDTH = 900
DEFAULT_IMAGE_URL = "/sample_image.png"
DEFAULT_LABELS = "Object A,Object B,Background"


@dataclass(frozen=True)
class ImageMeta:
    width: int
    height: int


def _fetch_image_meta(url: str) -> ImageMeta:
    """Fetch image metadata from URL. Cache disabled for debugging."""
    # Handle relative URLs by converting to absolute
    if url.startswith("/"):
        url = f"http://127.0.0.1:8000{url}"

    with urllib.request.urlopen(url) as response:
        data = response.read()
    with Image.open(BytesIO(data)) as img:
        width, height = img.size
    return ImageMeta(width, height)


async def fetch_image_meta(url: str) -> ImageMeta:
    return await asyncio.to_thread(_fetch_image_meta, url)


def clamp(value: int, min_value: int, max_value: int) -> int:
    if max_value <= min_value:
        return min_value
    return max(min_value, min(value, max_value))


def compute_rect(
    start: Optional[Dict[str, int]], pointer: Optional[Dict[str, int]]
) -> Optional[Dict[str, int]]:
    if not start or not pointer:
        return None
    x1 = min(start["x"], pointer["x"])
    x2 = max(start["x"], pointer["x"])
    y1 = min(start["y"], pointer["y"])
    y2 = max(start["y"], pointer["y"])
    return {
        "left": x1,
        "top": y1,
        "width": x2 - x1 + 1,
        "height": y2 - y1 + 1,
    }


def labels_from_text(text: str) -> List[str]:
    return [label.strip() for label in text.split(",") if label.strip()]


@component
def BBoxAnnotatorApp():
    url_text, set_url_text = use_state(DEFAULT_IMAGE_URL)
    image_url, set_image_url = use_state(DEFAULT_IMAGE_URL)
    labels_text, set_labels_text = use_state(DEFAULT_LABELS)
    input_method, set_input_method = use_state("select")
    entries, set_entries = use_state([])  # type: ignore[var-annotated]
    status, set_status = use_state("free")
    start_pos, set_start_pos = use_state(None)
    pointer, set_pointer = use_state(None)
    image_meta, set_image_meta = use_state(None)
    display_size, set_display_size = use_state({"width": 0, "height": 0})
    scale, set_scale = use_state(1.0)
    label_value, set_label_value = use_state("")
    error_message, set_error_message = use_state("")

    # Load image metadata asynchronously when URL changes
    @use_effect(dependencies=[image_url])
    async def load_image_metadata():
        set_error_message("")
        try:
            meta = await fetch_image_meta(image_url)
            factor = min(1.0, MAX_DISPLAY_WIDTH / meta.width) if meta.width else 1.0
            set_scale(factor)
            set_image_meta(meta)
            set_display_size(
                {
                    "width": int(meta.width * factor),
                    "height": int(meta.height * factor),
                }
            )
            set_status("free")
            set_start_pos(None)
            set_pointer(None)
            set_label_value("")
        except Exception as exc:
            set_error_message(f"Failed to load image: {exc}")
            set_image_meta(None)
            set_display_size({"width": 0, "height": 0})

    def normalized_entry(entry: Dict) -> Dict:
        factor = 1.0 if scale == 0 else 1 / scale
        rect = entry["rect"]
        return {
            "left": int(round(rect["left"] * factor)),
            "top": int(round(rect["top"] * factor)),
            "width": int(round(rect["width"] * factor)),
            "height": int(round(rect["height"] * factor)),
            "label": entry["label"],
        }

    def handle_mouse_down(evt):
        if status not in ("free", "input"):
            return
        if not display_size["width"] or evt.get("button") == 2:
            return
        point = {
            "x": clamp(int(evt.get("offsetX", 0)), 0, display_size["width"] - 1),
            "y": clamp(int(evt.get("offsetY", 0)), 0, display_size["height"] - 1),
        }
        set_start_pos(point)
        set_pointer(point)
        set_status("hold")

    def handle_mouse_move(evt):
        if status != "hold" or not display_size["width"]:
            return
        point = {
            "x": clamp(int(evt.get("offsetX", 0)), 0, display_size["width"] - 1),
            "y": clamp(int(evt.get("offsetY", 0)), 0, display_size["height"] - 1),
        }
        set_pointer(point)

    def handle_mouse_up(evt):
        if status != "hold" or not display_size["width"]:
            return
        point = {
            "x": clamp(int(evt.get("offsetX", 0)), 0, display_size["width"] - 1),
            "y": clamp(int(evt.get("offsetY", 0)), 0, display_size["height"] - 1),
        }
        set_pointer(point)
        set_status("input")

    rect = compute_rect(start_pos, pointer)
    label_options = labels_from_text(labels_text) or ["object"]

    def clear_draft():
        set_status("free")
        set_start_pos(None)
        set_pointer(None)
        set_label_value("")

    def add_entry(label: str):
        if not rect or not label.strip():
            clear_draft()
            return
        entry = {
            "id": str(uuid.uuid4()),
            "label": label.strip(),
            "rect": rect,
        }
        set_entries([*entries, entry])
        clear_draft()

    def delete_entry(entry_id: str):
        set_entries([entry for entry in entries if entry["id"] != entry_id])

    canvas_children = []
    if rect and status in ("hold", "input"):
        canvas_children.append(
            html.div(
                {
                    "style": {
                        "position": "absolute",
                        "left": f"{rect['left']}px",
                        "top": f"{rect['top']}px",
                        "width": f"{rect['width']}px",
                        "height": f"{rect['height']}px",
                        "border": "2px dotted rgb(127,255,127)",
                        "background": "rgba(127,255,127,0.08)",
                    }
                }
            )
        )

    for entry in entries:
        box = html.div(
            {
                "style": {
                    "position": "absolute",
                    "left": f"{entry['rect']['left']}px",
                    "top": f"{entry['rect']['top']}px",
                    "width": f"{entry['rect']['width']}px",
                    "height": f"{entry['rect']['height']}px",
                    "border": "2px solid rgb(255,0,0)",
                    "color": "rgb(255,0,0)",
                    "fontFamily": "monospace",
                    "fontSize": "12px",
                    "boxSizing": "border-box",
                    "background": "rgba(255,255,255,0.05)",
                }
            },
            html.button(
                {
                    "style": {
                        "position": "absolute",
                        "top": "-10px",
                        "right": "-10px",
                        "width": "20px",
                        "height": "20px",
                        "borderRadius": "50%",
                        "border": "1px solid #fff",
                        "background": "#030",
                        "color": "#fff",
                        "cursor": "pointer",
                        "lineHeight": "18px",
                        "padding": "0",
                        "fontSize": "12px",
                        "zIndex": "10",
                    },
                    "onMouseDown": event(lambda evt: None, stop_propagation=True),
                    "onClick": event(
                        lambda e, entry_id=entry["id"]: delete_entry(entry_id),
                        stop_propagation=True,
                        prevent_default=True,
                    ),
                },
                "x"
            ),
            html.div(
                {
                    "style": {
                        "position": "absolute",
                        "bottom": "-18px",
                        "left": "0",
                        "background": "rgba(0,0,0,0.5)",
                        "color": "white",
                        "padding": "2px 4px",
                        "fontSize": "12px",
                    }
                },
                entry["label"]
            ),
        )
        canvas_children.append(box)

    input_form = None
    if rect and status == "input":
        shared_style = {
            "position": "absolute",
            "left": f"{rect['left']}px",
            "top": f"{rect['top'] + rect['height'] + 6}px",
            "background": "rgba(0,0,0,0.7)",
            "color": "#fff",
            "padding": "8px",
            "display": "flex",
            "gap": "6px",
            "alignItems": "center",
            "borderRadius": "4px",
        }

        if input_method == "select":
            input_form = html.div(
                {"style": shared_style},
                html.select(
                    {
                        "value": "",
                        "autoFocus": True,
                        "onChange": event(
                            lambda evt: add_entry(
                                evt.get("target", {}).get("value", "") or ""
                            )
                        ),
                        "onMouseDown": event(lambda evt: None, stop_propagation=True),
                    },
                    html.option(
                        {"value": "", "disabled": True, "selected": True},
                        "choose an item",
                    ),
                    *[html.option({"value": label}, label) for label in label_options],
                ),
                html.button(
                    {
                        "onClick": event(lambda evt: clear_draft()),
                        "style": {"cursor": "pointer"},
                    },
                    "Cancel"
                ),
            )
        else:
            input_form = html.div(
                {"style": shared_style},
                html.input(
                    {
                        "type": "text",
                        "value": label_value,
                        "autoFocus": True,
                        "onChange": event(
                            lambda evt: set_label_value(
                                evt.get("target", {}).get("value", "")
                            )
                        ),
                        "onKeyDown": event(
                            lambda evt: add_entry(label_value)
                            if evt.get("key") == "Enter"
                            else None
                        ),
                        "onMouseDown": event(lambda evt: None, stop_propagation=True),
                        "style": {"minWidth": "140px"},
                    }
                ),
                html.button(
                    {
                        "onClick": event(lambda evt: add_entry(label_value)),
                        "style": {"cursor": "pointer"},
                    },
                    "Add"
                ),
                html.button(
                    {
                        "onClick": event(lambda evt: clear_draft()),
                        "style": {"cursor": "pointer"},
                    },
                    "Cancel"
                ),
            )

    if input_form:
        canvas_children.append(input_form)

    normalized_entries = [normalized_entry(entry) for entry in entries]

    canvas = html.div(
        {
            "style": {
                "position": "relative",
                "width": f"{display_size['width']}px" if display_size["width"] else "720px",
                "height": f"{display_size['height']}px" if display_size["height"] else "440px",
                "backgroundImage": f"url({image_url})",
                "backgroundSize": "100% 100%" if display_size["width"] else "contain",
                "backgroundRepeat": "no-repeat",
                "border": "1px solid #444",
                "cursor": "crosshair",
                "overflow": "hidden",
                "userSelect": "none",
            },
            "onMouseDown": event(handle_mouse_down),
            "onMouseMove": event(handle_mouse_move),
            "onMouseUp": event(handle_mouse_up),
        },
        *canvas_children,
    )

    control_panel = html.div(
        {
            "style": {
                "display": "flex",
                "flexDirection": "column",
                "gap": "8px",
                "width": "320px",
            }
        },
        html.div(
            {"style": {"display": "flex", "flexDirection": "column", "gap": "4px"}},
            html.label("Image URL"),
            html.input(
                {
                    "type": "text",
                    "value": url_text,
                    "onChange": event(
                        lambda evt: set_url_text(evt.get("target", {}).get("value", ""))
                    ),
                    "style": {"width": "100%"},
                }
            ),
            html.button(
                {
                    "onClick": event(lambda evt: set_image_url(url_text.strip())),
                    "style": {"cursor": "pointer", "width": "120px"},
                },
                "Load image"
            ),
        ),
        html.div(
            {"style": {"display": "flex", "flexDirection": "column", "gap": "4px"}},
            html.label("Label candidates (comma separated)"),
            html.textarea(
                {
                    "value": labels_text,
                    "rows": 3,
                    "onChange": event(
                        lambda evt: set_labels_text(
                            evt.get("target", {}).get("value", "")
                        )
                    ),
                }
            ),
        ),
        html.div(
            {"style": {"display": "flex", "gap": "8px", "alignItems": "center"}},
            html.label("Input method:"),
            html.select(
                {
                    "value": input_method,
                    "onChange": event(
                        lambda evt: set_input_method(
                            evt.get("target", {}).get("value", "text")
                        )
                    ),
                },
                html.option({"value": "text"}, "text"),
                html.option({"value": "select"}, "select"),
            ),
        ),
        html.div(
            {"style": {"display": "flex", "gap": "8px"}},
            html.button(
                {
                    "onClick": event(lambda evt: set_entries([])),
                    "style": {"cursor": "pointer"},
                },
                "Reset entries"
            ),
        ),
        html.div(
            {
                "style": {
                    "fontSize": "12px",
                    "color": "#ccc",
                    "lineHeight": "16px",
                }
            },
            f"Image natural size: "
            f"{image_meta.width if image_meta else '?'} x "
            f"{image_meta.height if image_meta else '?'} px",
            html.br(),
            f"Display size: {display_size['width']} x {display_size['height']} px",
            html.br(),
            f"Entries: {len(entries)}",
        ),
        html.div(
            {
                "style": {
                    "color": "#e66",
                    "minHeight": "18px",
                    "fontSize": "12px",
                }
            },
            error_message,
        ),
    )

    entries_view = html.pre(
        {
            "style": {
                "background": "#0f172a",
                "color": "#e2e8f0",
                "padding": "12px",
                "borderRadius": "6px",
                "fontSize": "12px",
                "height": "100%",
                "overflow": "auto",
                "minHeight": "240px",
            }
        },
        json.dumps(normalized_entries, indent=2),
    )

    return html.div(
        {
            "style": {
                "fontFamily": "Inter, system-ui, sans-serif",
                "background": "#0b1021",
                "color": "#e2e8f0",
                "minHeight": "100vh",
                "padding": "16px",
                "boxSizing": "border-box",
            }
        },
        html.h2("ReactPy Bounding Box Annotator"),
        html.div(
            {
                "style": {
                    "display": "grid",
                    "gridTemplateColumns": "340px 1fr 320px",
                    "gap": "16px",
                    "alignItems": "start",
                }
            },
            control_panel,
            canvas,
            entries_view,
        ),
    )


fastapi_app = FastAPI()


@fastapi_app.get("/sample_image.png")
async def get_sample_image():
    """Generate a sample image for testing."""
    # Create 800x600 image with gradient background
    img = Image.new('RGB', (800, 600), color=(73, 109, 137))
    draw = ImageDraw.Draw(img)

    # Draw some shapes for visual reference
    draw.rectangle([100, 100, 300, 300], fill=(200, 100, 100), outline=(255, 255, 255), width=3)
    draw.ellipse([400, 150, 650, 400], fill=(100, 200, 100), outline=(255, 255, 255), width=3)
    draw.polygon([(200, 450), (350, 500), (150, 550)], fill=(100, 100, 200), outline=(255, 255, 255))

    # Add text
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
    except:
        font = ImageFont.load_default()
    draw.text((250, 30), "Sample Image", fill=(255, 255, 255), font=font)

    # Convert to bytes
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")


configure(fastapi_app, BBoxAnnotatorApp)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:fastapi_app", host="0.0.0.0", port=8000, reload=True)
