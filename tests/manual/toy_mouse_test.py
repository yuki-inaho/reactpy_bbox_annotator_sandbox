"""
Toy problem to debug mouse interaction events in ReactPy.
This isolates the issue: Are mouse events (onMouseDown/Move/Up) working correctly?
Run with: uv run uvicorn toy_mouse_test:app --host 127.0.0.1 --port 8003
"""

from fastapi import FastAPI
from reactpy import component, html, use_state
from reactpy.backend.fastapi import configure
from reactpy.core.events import event


@component
def ToyMouseApp():
    """Minimal mouse interaction test to isolate event handling."""
    status, set_status = use_state("waiting")
    start_pos, set_start_pos = use_state(None)
    end_pos, set_end_pos = use_state(None)
    current_pos, set_current_pos = use_state(None)
    event_log, set_event_log = use_state([])

    def add_log(message):
        """Add message to event log."""
        new_log = event_log + [message]
        set_event_log(new_log[-10:])  # Keep last 10 events
        print(f"[ToyMouse] {message}")

    def handle_mouse_down(evt):
        """Handle mouse down event."""
        x = evt.get("offsetX", -1)
        y = evt.get("offsetY", -1)
        button = evt.get("button", -1)

        add_log(f"MouseDown: offsetX={x}, offsetY={y}, button={button}")

        set_start_pos({"x": x, "y": y})
        set_current_pos({"x": x, "y": y})
        set_end_pos(None)
        set_status("dragging")

    def handle_mouse_move(evt):
        """Handle mouse move event."""
        if status != "dragging":
            return

        x = evt.get("offsetX", -1)
        y = evt.get("offsetY", -1)

        add_log(f"MouseMove: offsetX={x}, offsetY={y}")

        set_current_pos({"x": x, "y": y})

    def handle_mouse_up(evt):
        """Handle mouse up event."""
        if status != "dragging":
            return

        x = evt.get("offsetX", -1)
        y = evt.get("offsetY", -1)

        add_log(f"MouseUp: offsetX={x}, offsetY={y}")

        set_end_pos({"x": x, "y": y})
        set_status("completed")

    def reset():
        """Reset state."""
        set_status("waiting")
        set_start_pos(None)
        set_end_pos(None)
        set_current_pos(None)
        set_event_log([])
        print("[ToyMouse] Reset")

    # Calculate rectangle if dragging or completed
    rect_info = None
    if start_pos and current_pos:
        left = min(start_pos["x"], current_pos["x"])
        top = min(start_pos["y"], current_pos["y"])
        width = abs(current_pos["x"] - start_pos["x"])
        height = abs(current_pos["y"] - start_pos["y"])
        rect_info = {"left": left, "top": top, "width": width, "height": height}

    # Canvas children
    canvas_children = []
    if rect_info and rect_info["width"] > 5 and rect_info["height"] > 5:
        color = (
            "rgba(127,255,127,0.3)" if status == "dragging" else "rgba(255,127,127,0.3)"
        )
        border_color = (
            "rgb(127,255,127)" if status == "dragging" else "rgb(255,127,127)"
        )

        canvas_children.append(
            html.div(
                {
                    "style": {
                        "position": "absolute",
                        "left": f"{rect_info['left']}px",
                        "top": f"{rect_info['top']}px",
                        "width": f"{rect_info['width']}px",
                        "height": f"{rect_info['height']}px",
                        "border": f"2px dashed {border_color}",
                        "background": color,
                        "pointerEvents": "none",
                    }
                }
            )
        )

    # Canvas element
    canvas = html.div(
        {
            "style": {
                "position": "relative",
                "width": "600px",
                "height": "400px",
                "border": "2px solid #333",
                "cursor": "crosshair",
                "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                "userSelect": "none",
            },
            "onMouseDown": event(handle_mouse_down),
            "onMouseMove": event(handle_mouse_move),
            "onMouseUp": event(handle_mouse_up),
            "data-testid": "mouse-canvas",
        },
        *canvas_children,
    )

    # Status display
    status_color = {
        "waiting": "gray",
        "dragging": "blue",
        "completed": "green",
    }.get(status, "black")

    return html.div(
        {"style": {"padding": "20px", "fontFamily": "sans-serif"}},
        html.h1("Toy Mouse Interaction Test"),
        html.div(
            {"style": {"marginBottom": "10px"}},
            html.span(
                {"style": {"fontWeight": "bold", "color": status_color}},
                f"Status: {status}",
            ),
            html.button(
                {
                    "onClick": event(lambda e: reset()),
                    "style": {"marginLeft": "20px", "cursor": "pointer"},
                },
                "Reset",
            ),
        ),
        html.div({"style": {"marginBottom": "20px"}}, canvas),
        html.div(
            {
                "style": {
                    "display": "grid",
                    "gridTemplateColumns": "1fr 1fr",
                    "gap": "10px",
                }
            },
            html.div(
                html.h3("Mouse Data:"),
                html.pre(
                    {"style": {"fontSize": "12px"}},
                    f"Start: {start_pos}\n"
                    f"Current: {current_pos}\n"
                    f"End: {end_pos}\n"
                    f"Rect: {rect_info}",
                ),
            ),
            html.div(
                html.h3("Event Log (last 10):"),
                html.pre(
                    {
                        "style": {
                            "fontSize": "12px",
                            "height": "200px",
                            "overflow": "auto",
                        }
                    },
                    "\n".join(event_log) if event_log else "(no events yet)",
                ),
            ),
        ),
    )


fastapi_app = FastAPI()
configure(fastapi_app, ToyMouseApp)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("toy_mouse_test:fastapi_app", host="0.0.0.0", port=8003, reload=True)
