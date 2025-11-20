# justfile for ReactPy BBox Annotator
# Run `just --list` to see all available recipes

# Default recipe: show help
default:
    @just --list

# Start the development server with hot reload
serve:
    uv run uvicorn app:fastapi_app --host 127.0.0.1 --port 8000 --reload

# Start the server on all interfaces (for remote access)
serve-remote:
    uv run uvicorn app:fastapi_app --host 0.0.0.0 --port 8000 --reload

# Run E2E tests only
test-e2e:
    uv run pytest tests/e2e/test_bbox.py -v

# Run all tests
test-all:
    uv run pytest -v

# Run tests in headless mode with xvfb (for CI)
test-ci:
    xvfb-run --auto-servernum --server-args='-screen 0 1280x720x24' \
        uv run pytest tests/e2e/test_bbox.py -v

# Install Python dependencies
install:
    uv pip install -e .
    uv pip install playwright pytest pytest-asyncio

# Install Playwright browsers
install-playwright:
    uv run playwright install-deps chromium
    uv run playwright install chromium

# Full setup: install dependencies and browsers
setup: install install-playwright

# Clean up Python cache files
clean:
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

# Run linting (if ruff is installed)
lint:
    @if command -v ruff >/dev/null 2>&1; then \
        uv run ruff check .; \
    else \
        echo "ruff not installed. Install with: uv pip install ruff"; \
    fi

# Format code (if ruff is installed)
format:
    @if command -v ruff >/dev/null 2>&1; then \
        uv run ruff check --fix .; \
        uv run ruff format .; \
    else \
        echo "ruff not installed. Install with: uv pip install ruff"; \
    fi

# Check for security vulnerabilities (if safety is installed)
security:
    @if command -v safety >/dev/null 2>&1; then \
        uv run safety check; \
    else \
        echo "safety not installed. Install with: uv pip install safety"; \
    fi

# Show project information
info:
    @echo "ReactPy BBox Annotator"
    @echo "====================="
    @echo ""
    @echo "Python version:"
    @python --version
    @echo ""
    @echo "Installed packages:"
    @uv pip list | grep -E "(reactpy|fastapi|playwright|pytest)"
    @echo ""
    @echo "Project structure:"
    @tree -L 2 -I '__pycache__|*.egg-info|.pytest_cache|.venv' . || ls -la

# Development mode: run server in background and watch for changes
dev:
    @echo "Starting development mode..."
    @echo "Server will run on http://127.0.0.1:8000"
    @echo "Press Ctrl+C to stop"
    just serve
