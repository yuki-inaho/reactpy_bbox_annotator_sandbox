# ReactPy BBox Annotator

A web-based bounding box annotation tool built with ReactPy and FastAPI.
Create, edit, and export bounding box annotations for images with an intuitive drag-and-drop interface.

## Features

- **Interactive Drawing**: Draw bounding boxes by clicking and dragging on images
- **Flexible Labeling**: Choose between select dropdown or text input for labels
- **Image Support**: Load images from URLs or local server endpoints
- **Real-time Preview**: See your annotations as you draw them
- **Export Ready**: JSON export with normalized coordinates for machine learning workflows
- **Security Features**:
  - SSRF protection with URL validation
  - DoS protection with image size limits (10MB max)
  - Input sanitization for labels and URLs

## Technology Stack

- **Frontend**: ReactPy 1.1.0 (Python-based reactive web framework)
- **Backend**: FastAPI (ASGI web server)
- **Testing**: Playwright (E2E browser testing)
- **Package Manager**: uv (fast Python package installer)

## Prerequisites

- Python 3.11+
- uv (Python package manager)
- System libraries for Playwright (installed via apt)

## Setup

### 1. System Dependencies

Install required system packages for Playwright:

```bash
sudo apt-get update
sudo apt-get install -y \
  wget ca-certificates libnss3 libatk1.0-0 libatk-bridge2.0-0 \
  libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 \
  libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 xvfb
```

### 2. Python Environment

Create and activate a virtual environment with uv:

```bash
uv venv .venv
source .venv/bin/activate
```

### 3. Install Python Dependencies

```bash
uv pip install -e .
uv pip install playwright pytest pytest-asyncio
```

### 4. Install Playwright Browsers

```bash
uv run playwright install-deps chromium
uv run playwright install chromium
```

## Usage

### Running the Application

Start the development server:

```bash
uv run uvicorn app:fastapi_app --host 127.0.0.1 --port 8000 --reload
```

Open your browser and navigate to:
```
http://127.0.0.1:8000
```

### Using the Annotator

1. **Load an Image**:
   - Enter an image URL in the "Image URL" field
   - Click "Load image" button
   - Default sample image is available at `/sample_image.png`

2. **Configure Labels**:
   - Edit the comma-separated labels in the "Label candidates" textarea
   - Default labels: "Object A, Object B, Background"

3. **Choose Input Method**:
   - **Select**: Choose from dropdown (faster for predefined labels)
   - **Text**: Type custom labels (more flexible)

4. **Draw Annotations**:
   - Click and drag on the image to create a bounding box
   - Release mouse to enter label input mode
   - Select or type a label
   - Click "Cancel" to discard the current box

5. **Manage Entries**:
   - Click the "x" button on any box to delete it
   - Click "Reset entries" to clear all annotations

6. **Export**:
   - View JSON output in the right panel
   - Coordinates are normalized to original image dimensions

## Testing

### Run E2E Tests

```bash
uv run pytest tests/e2e/test_bbox.py -v
```

### Run All Tests

```bash
uv run pytest -v
```

### Test Coverage

Current E2E test coverage:
- Basic UI rendering
- Select mode annotation
- Text mode annotation
- Entry deletion
- Reset entries
- Image URL change
- Input cancellation

## Project Structure

```
.
├── app.py                    # Main application (FastAPI + ReactPy)
├── pyproject.toml            # Python project configuration
├── pytest.ini                # Pytest configuration
├── tests/
│   ├── conftest.py           # Pytest fixtures
│   └── e2e/
│       └── test_bbox.py      # E2E tests (7 tests)
├── docs/
│   ├── workdoc.md            # Work log and planning
│   └── code_review.md        # Code review report
└── README.md                 # This file
```

## Architecture

### State Management

The application uses ReactPy's `use_state` hooks for state management:

- **url_text**: Image URL input field value
- **image_url**: Currently loaded image URL
- **labels_text**: Comma-separated labels configuration
- **input_method**: "select" or "text" mode
- **entries**: List of annotation entries
- **status**: Current interaction state ("free", "hold", "input")
- **start_pos/pointer**: Mouse positions for drawing
- **image_meta**: Image dimensions
- **display_size**: Scaled display dimensions
- **scale**: Display scale factor
- **label_value**: Text input value
- **error_message**: Error display message

### State Transitions

```
free -> hold: User clicks to start drawing
hold -> hold: User drags to define box size
hold -> input: User releases mouse to finish box
input -> free: User confirms label or cancels
```

### Security

#### SSRF Protection

- Protocol whitelist: `http`, `https` only
- Hostname blocklist: `localhost`, `127.0.0.1`, AWS/GCP metadata services
- Private IP range blocking: RFC 1918, loopback, link-local addresses
- Relative URLs bypass check (trusted local server)

#### DoS Protection

- Image size limit: 10MB maximum
- Content-Length header validation
- Read size limit enforcement
- Network timeout: 10 seconds

## Development

### Code Quality Principles

This project follows:
- **DRY** (Don't Repeat Yourself): Extract common patterns into reusable functions
- **KISS** (Keep It Simple, Stupid): Prefer simple, readable solutions
- **SOLID**: Single responsibility, clear interfaces
- **TDD**: Tests written before implementation

### Adding New Features

1. Write E2E test first (TDD approach)
2. Implement feature in `app.py`
3. Ensure all tests pass
4. Update documentation

## Known Limitations

- Maximum image size: 10MB
- Only supports public HTTP/HTTPS image URLs (no local file upload)
- No persistent storage (annotations lost on page refresh)
- No undo/redo functionality
- No zoom/pan for large images

## Future Improvements

- [ ] Add test helper functions to reduce test code duplication
- [ ] Implement undo/redo functionality
- [ ] Add keyboard shortcuts for common operations
- [ ] Support image file upload
- [ ] Add persistent storage (database or localStorage)
- [ ] Implement zoom and pan for large images
- [ ] Add more export formats (COCO, YOLO, Pascal VOC)

## License

This project is provided as-is for educational purposes.

## Contributing

1. Follow the existing code style
2. Add tests for new features
3. Ensure all tests pass before submitting
4. Update documentation as needed
