# BRIEF: decksmith

> A command-line application to dynamically generate decks of cards from a YAML specification and a CSV data file, inspired by nandeck.

## 1. Overview (README)

```markdown
# DeckSmith

[julynx.github.io/decksmith](https://julynx.github.io/decksmith/)

*A powerful application to dynamically generate decks of cards from a YAML specification and a CSV data file.*

<a href="https://github.com/Julynx/decksmith/releases/latest/download/DeckSmith_Setup.exe" target="_blank">
<img src="https://i.imgur.com/cSWO5Ta.png" height="64">
</a><br><br>

<p align="center">
  <img src="https://raw.githubusercontent.com/Julynx/decksmith/refs/heads/main/docs/assets/screenshot.png" width='100%'>
</p>

<br>

DeckSmith is ideal for automating the creation of all kinds of decks, including TCG decks, tarot decks, business cards, and even slides.

## Why DeckSmith?

... (truncated) [Read more](file:///D:/_DISK_/_Documentos_/Mis_repositorios/decksmith/docs/README.md)
```

## 2. Dependencies

```text
click
crossfiledialog>=1.1.0
flask>=3.1.2
jval==1.0.6
pandas
pillow>=11.3.0
platformdirs>=4.5.1
pywin32>=311; sys_platform == 'win32'
reportlab>=4.4.3
ruamel-yaml>=0.19.1
toml>=0.10.2
waitress>=3.0.2
```

## 3. Directory Structure

```text
decksmith/
├── assets
├── decksmith
    ├── gui
        ├── static
            ├── css
            ├── img
            └── js
        ├── templates
            └── index.html
        ├── __init__.py
        └── app.py
    ├── renderers
        ├── __init__.py
        ├── image.py
        ├── shapes.py
        └── text.py
    ├── templates
        ├── deck.csv
        └── deck.yaml
    ├── __init__.py
    ├── card_builder.py
    ├── deck_builder.py
    ├── export.py
    ├── image_ops.py
    ├── logger.py
    ├── macro.py
    ├── main.py
    ├── project.py
    ├── utils.py
    └── validate.py
├── docs
    ├── assets
        ├── card_1.png
        ├── card_2.png
        ├── decksmith.ico
        └── screenshot.png
    ├── DEVELOPMENT.md
    ├── DOCS.md
    └── README.md
├── website
    ├── assets
        ├── card_1.png
        ├── card_2.png
        ├── decksmith.ico
        └── screenshot.png
    ├── css
        └── style.css
    ├── docs.html
    ├── index.html
    ├── robots.txt
    └── sitemap.xml
├── .gitignore
├── .project-actions.json
├── .python-version
├── build.py
├── installer.cfg
├── pyproject.toml
└── uv.lock
```

## 4. Import Tree

```text
- build.py

- decksmith\__init__.py

- decksmith\gui\__init__.py

- decksmith\main.py
  - decksmith\deck_builder.py
    - decksmith\card_builder.py
      - decksmith\logger.py
      - decksmith\renderers\image.py
        - decksmith\image_ops.py
        - decksmith\utils.py
      - decksmith\renderers\shapes.py
        - decksmith\utils.py
      - decksmith\renderers\text.py
        - decksmith\utils.py
      - decksmith\utils.py
      - decksmith\validate.py
    - decksmith\logger.py
    - decksmith\macro.py
  - decksmith\export.py
    - decksmith\logger.py
  - decksmith\gui\app.py
    - decksmith\card_builder.py (...)
    - decksmith\deck_builder.py (...)
    - decksmith\export.py (...)
    - decksmith\logger.py
    - decksmith\macro.py
    - decksmith\project.py
  - decksmith\logger.py

- decksmith\renderers\__init__.py
```

## 5. Module Definitions

### build.py

```text
- def get_dependencies()
  """
  Extract dependencies from uv export.
  """
- def main()
  """
  Builds the DeckSmith installer executable.
  """
```

### decksmith\card_builder.py

```text
- class CardBuilder
  """
  A class to build a card image based on a YAML specification.
  Attributes:
      spec (Dict[str, Any]): The YAML specification for the card.
      card (Image.Image): The PIL Image object representing the card.
      draw (ImageDraw.ImageDraw): The PIL ImageDraw object for drawing on the card.
      element_positions (Dict[str, Tuple[int, int, int, int]]):
          A dictionary mapping element IDs to their bounding boxes.
  """
  - def render(self)
    """
    Renders the card image by drawing all elements specified in the YAML.
    
    Returns:
        Image.Image: The rendered card image.
    
    Raises:
        Exception: If an error occurs during rendering.
    """
  - def build(self, output_path: Path)
    """
    Builds the card image and saves it to the specified path.
    
    Args:
        output_path (Path): The path where the card image will be saved.
    """
```

### decksmith\deck_builder.py

```text
- class DeckBuilder
  """
  A class to build a deck of cards based on a YAML specification and a CSV file.
  Attributes:
      spec_path (Path): Path to the YAML specification file.
      csv_path (Union[Path, None]): Path to the CSV file containing card data.
      cards (list): List of CardBuilder instances for each card in the deck.
  """
  - def spec(self)
    """
    Loads and caches the spec file.
    """
  - def build_deck(self, output_path: Path)
    """
    Builds the deck of cards by reading the CSV file and creating CardBuilder
    instances.
    
    Args:
        output_path (Path): The directory path to save the built cards.
    """
```

### decksmith\export.py

```text
- class PdfExporter
  """
  A class to export images from a folder to a PDF file.
  """
  - def export(self)
    """
    Exports the images to a PDF file.
    """
```

### decksmith\image_ops.py

```text
- class ImageOps
  """
  A class to handle image processing operations.
  """
  - def apply_filters(img: Image.Image, filters: Dict[str, Any])
    """
    Applies a set of filters to an image.
    Args:
        img (Image.Image): The image to process.
        filters (Dict[str, Any]): A dictionary of filters to apply.
    Returns:
        Image.Image: The processed image.
    """
```

### decksmith\logger.py

```text
- def setup_logging(log_file: str, level: int)
  """
  Sets up the logging configuration.
  """
```

### decksmith\macro.py

```text
- class MacroResolver
  """
  A class to resolve macros in card specifications.
  """
  - def resolve(spec: Dict[str, Any], row: Dict[str, Any])
    """
    Replaces %colname% macros in the card specification with values from the row.
    Works recursively for nested structures.
    Args:
        spec (dict): The card specification.
        row (dict): A dictionary representing a row from the CSV file.
    Returns:
        dict: The updated card specification with macros replaced.
    """
```

### decksmith\main.py

```text
- def cli(ctx, gui)
  """
  A command-line tool for building decks of cards.
  """
- def init()
  """
  Initializes a new project by creating deck.yaml and deck.csv.
  """
- def build(ctx, output, spec, data)
  """
  Builds the deck of cards.
  """
- def export(ctx, image_folder, output, page_size, width, height, gap, margins)
  """
  Exports images from a folder to a PDF file.
  """
```

### decksmith\project.py

```text
- class ProjectManager
  """
  A class to manage decksmith projects.
  """
  - def set_working_dir(self, path: Path)
    """
    Sets the working directory.
    """
  - def get_working_dir(self)
    """
    Returns the current working directory.
    """
  - def close_project(self)
    """
    Closes the current project.
    """
  - def create_project(self, path: Path)
    """
    Creates a new project at the specified path.
    
    Args:
        path (Path): The path where the project directory will be created.
    """
  - def load_files(self)
    """
    Loads the deck.yaml and deck.csv files from the current project.
    
    Returns:
        Dict[str, str]: A dictionary with keys "yaml" and "csv"
        containing file contents.
    """
  - def save_files(self, yaml_content: Optional[str], csv_content: Optional[str])
    """
    Saves the deck.yaml and deck.csv files to the current project.
    
    Args:
        yaml_content (Optional[str]): The content of the deck.yaml file.
        csv_content (Optional[str]): The content of the deck.csv file.
    
    Raises:
        ValueError: If no project is currently selected (working_dir is None).
    """
```

### decksmith\utils.py

```text
- def get_wrapped_text(text: str, font: ImageFont.ImageFont, line_length: int) -> str
  """
  Wraps text to fit within a specified line length using the given font,
  preserving existing newlines.
  Args:
      text (str): The text to wrap.
      font (ImageFont.ImageFont): The font to use for measuring text length.
      line_length (int): The maximum length of each line in pixels.
  
  Returns:
      str: The wrapped text with newlines inserted where necessary.
  """
- def apply_anchor(size: Tuple[int, ...], anchor: str) -> Tuple[int, int]
  """
  Applies an anchor to a size tuple to determine the position of an element.
  Args:
      size (Tuple[int, ...]): A tuple representing the size (width, height)
          or a bounding box (x1, y1, x2, y2).
      anchor (str): The anchor position, e.g., "center", "top-left".
  Returns:
      Tuple[int, int]: A tuple representing the position (x, y) based on the anchor.
  """
- def int_tuple(tuple_value: Tuple[any, ...]) -> Tuple[int, ...]
  """
  Converts a tuple of any type to a tuple of integers.
  Args:
      tuple_value (Tuple[any, ...]): The tuple to convert.
  Returns:
      Tuple[int, ...]: The converted tuple.
  """
```

### decksmith\validate.py

```text
- def validate_element(element: Dict[str, Any], element_type: str)
  """
  Validates an element of a card against a spec, raising an exception
  if it does not meet the spec.
  
  Args:
      element (dict): The card element.
      element_type (str): The type of the element
  
  Raises:
      ValueError: If the element type is unknown.
      jval.exceptions.ValidationException: If the element does not match the spec.
  """
- def validate_card(card: Dict[str, Any])
  """
  Validates a card against a spec, raising an exception
  if it does not meet the spec.
  
  Args:
      card (Dict[str, Any]): The card.
  
  Raises:
      jval.exceptions.ValidationException: If the card does not match the spec.
  """
- def transform_card(card: Dict[str, Any]) -> Dict[str, Any]
  """
  Perform certain automatic type casts on the card and its
  elements. For example, cast the "text" property of elements
  of type "text" to str, to support painting numbers as text.
  Args:
      card (Dict[str, Any]): The card.
  Return:
      Dict[str, Any]: The transformed card with all automatic casts applied.
  """
```

### decksmith\gui\app.py

```text
- class ServerState
  """
  Encapsulates the server's running state.
  """
- def signal_handler(sig, frame)
  """
  Handles system signals (e.g., SIGINT).
  """
- def events()
  """
  Streams server events to the client.
  """
- def index()
  """
  Renders the main page.
  """
- def get_current_project()
  """
  Returns the current project path.
  """
- def get_default_path()
  """
  Returns the default project path.
  """
- def browse_folder()
  """
  Opens a folder selection dialog.
  """
- def select_project()
  """
  Selects a project directory.
  """
- def close_project()
  """
  Closes the current project.
  """
- def create_project()
  """
  Creates a new project.
  """
- def load_files()
  """
  Loads project files.
  """
- def save_files()
  """
  Saves project files.
  """
- def list_cards()
  """
  Lists cards in the project.
  """
- def preview_card(card_index)
  """
  Previews a specific card.
  """
- def build_deck()
  """
  Builds the deck for the current project.
  """
- def export_pdf()
  """
  Exports the deck to PDF.
  """
- def open_browser()
  """
  Opens the browser.
  """
- def shutdown()
  """
  Shuts down the server.
  """
- def main()
  """
  Main entry point for the GUI.
  """
```

### decksmith\renderers\image.py

```text
- class ImageRenderer
  """
  A class to render image elements on a card.
  """
  - def render(self, card: Image.Image, element: Dict[str, Any], calculate_pos_func, store_pos_func)
    """
    Draws an image on the card.
    Args:
        card (Image.Image): The card image object.
        element (Dict[str, Any]): The image element specification.
        calculate_pos_func (callable): Function to calculate absolute position.
    Returns:
        Image.Image: The updated card image.
    """
```

### decksmith\renderers\shapes.py

```text
- class ShapeRenderer
  """
  A class to render shape elements on a card.
  """
  - def render(self, card: Image.Image, element: Dict[str, Any], calculate_pos_func, store_pos_func)
    """
    Draws a shape on the card.
    Args:
        card (Image.Image): The card image object.
        element (Dict[str, Any]): The shape element specification.
        calculate_pos_func (callable): Function to calculate absolute position.
        store_pos_func (callable): Function to store element position.
    Returns:
        Image.Image: The updated card image.
    """
```

### decksmith\renderers\text.py

```text
- class TextRenderer
  """
  A class to render text elements on a card.
  """
  - def render(self, card: Image.Image, element: Dict[str, Any], calculate_pos_func, store_pos_func)
    """
    Draws text on the card.
    Args:
        card (Image.Image): The card image object.
        element (Dict[str, Any]): The text element specification.
        calculate_pos_func (callable): Function to calculate absolute position.
        store_pos_func (callable): Function to store element position.
    Returns:
        Image.Image: The updated card image.
    """
```
