# ReactPy BBox Annotator

Web-based bounding box annotation tool built with ReactPy and FastAPI.

## Setup

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y wget ca-certificates libnss3 libatk1.0-0 libatk-bridge2.0-0 \
  libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
  libgbm1 libpango-1.0-0 libcairo2 xvfb

# Setup Python environment
uv venv .venv
source .venv/bin/activate
uv pip install -e .
uv pip install playwright pytest pytest-asyncio

# Install Playwright browser
uv run playwright install-deps chromium
uv run playwright install chromium
```

## Run

```bash
# Start server
uv run uvicorn app:fastapi_app --host 127.0.0.1 --port 8000 --reload

# Or using justfile
just serve
```

Access: http://127.0.0.1:8000

## Usage

1. Load image: Enter URL or use default `/sample_image.png`
2. Draw box: Click and drag on the image
3. Add label: Select from dropdown or type text
4. Delete: Click "x" button on box
5. Export: View JSON in right panel

## Test

```bash
# Run E2E tests
uv run pytest tests/e2e/test_bbox.py -v

# Or using justfile
just test-e2e
```
