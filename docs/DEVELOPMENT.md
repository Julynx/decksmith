# Development Guide

This document outlines the internal architecture of DeckSmith and provides guidelines for development.

## Architecture

DeckSmith is organized into several key modules:

### Core Logic (`decksmith/`)

-   **`main.py`**: The entry point for the CLI. Handles command-line arguments and launches the GUI.
-   **`card_builder.py`**: Orchestrates the creation of individual card images. It uses specific renderers for different element types.
-   **`deck_builder.py`**: Manages the creation of the entire deck. It reads the CSV data, resolves macros, and uses `CardBuilder` to generate images in parallel.
-   **`macro.py`**: Handles the resolution of macros (e.g., `%name%`) in the card specification using data from the CSV.
-   **`image_ops.py`**: Contains image processing operations (filters) like crop, resize, rotate, etc.
-   **`project.py`**: Manages project state, including working directory, file loading/saving, and project creation.
-   **`export.py`**: Handles exporting the generated images to a PDF file.
-   **`validate.py`**: Validates the card specification against a schema using `jval`.
-   **`utils.py`**: Utility functions.

### Renderers (`decksmith/renderers/`)

Rendering logic is split into specific classes for better modularity:

-   **`text.py`**: Handles text rendering, including font loading, wrapping, and positioning.
-   **`image.py`**: Handles image rendering, including loading and applying filters.
-   **`shapes.py`**: Handles shape rendering (circles, rectangles, polygons, etc.).

### GUI (`decksmith/gui/`)

-   **`app.py`**: A Flask application that serves the web-based GUI. It interacts with the core logic via `ProjectManager`, `DeckBuilder`, and `CardBuilder`.
-   **`static/`**: Contains static assets (CSS, JS).
-   **`templates/`**: Contains HTML templates.

## Adding New Features

### Adding a New Element Type

1.  Create a new renderer class in `decksmith/renderers/` (or add to an existing one if appropriate).
2.  Update `CardBuilder` to instantiate and use the new renderer.
3.  Update `decksmith/validate.py` to include the schema for the new element type.

### Adding a New Image Filter

1.  Add a new method `_filter_<name>` to `decksmith/image_ops.py`.
2.  Update `decksmith/validate.py` to include the new filter in the schema.

## Testing

Run tests using `pytest`:

```bash
uv run pytest
```
