# Documentation for PyDeck

## Getting started

### Installation

To begin, install PyDeck by opening a Terminal and entering `pip install pydeck`.

### pydeck init

Create a new folder and run `pydeck init` inside.

This will create two different files:
- `deck.json` defines the structure for the cards in the deck. The different elements that compose a card, such as text blocks, images, and shapes, are declared here, along with their sizes, positions, and other attributes. Edit this file with your favorite text editor to add and remove elements or modify their properties.
- `deck.csv` is a data file that holds the contents for the cards of the deck, with each row representing one card. The columns of this file represent dynamic fields that can be referenced in the JSON by name as `%column_name%`. Adding a new card to the deck is as easy as creating a new row in this file.

### `deck.json` syntax

The basic structure of a card is defined as:

```json
{
  "width": 250,
  "height": 350,
  "background_color": [255, 255, 255, 0],
  "elements": [
  ]
}
```

The `elements` array can contain objects of different types, such as `text`, `image`, `circle`, `rectangle`, etc.

#### Common attributes

All objects, regardless of their type, share the following attributes:

```json
{
    "id": "example-element",
    "type": "text | image | ..",
    "position": [0, 0],
    "relative_to": ["<id>", "<anchor>"],
    "anchor": "top-left | center | .."
}
```

#### Positioning

The `anchor` attribute defines the point or corner of the element that will be used to position it within the card.
For example, declaring an element with `"position": [50, 50]` and `"anchor": "center"` means the center of the object will be in the coordinates `[50, 50]`. Using an anchor of `bottom-left` will position the bottom-left corner of the object in that position instead.

The possible anchors are:
```
 top-left      | top-center    | top-right
---------------+---------------+---------------
 middle-left   | center        | middle-right
---------------+---------------+---------------
 bottom-left   | bottom-center | bottom-right
```

The `relative_to` attribute allows positioning elements relative to other elements by referencing their `id`, and an `anchor` point for the referenced element. The element will be positioned according to its own `anchor` and the `relative_to` anchor for the other element.

#### Text

An element of type `text` can have the following attributes:

```python
{
    "id": "example-text",
    "type": "text",
    "position": [0, 0],
    # Specific attributes:
    "text": "Hello, world!",
    "color": [0, 0, 0],
    "font_path": "arial.ttf",
    "font_size": 10,
    "font_variant": "Regular | Bold | ..",
    "line_spacing": 4,
    "width": 300,
    "align": "left | center | justify | ..",
    "stroke_width": 1,
    "stroke_color": [255, 255, 255]
}
```

The `line_spacing` attribute defines the vertical space in pixels between lines of text.

The `width` attribute limits the width in pixels for each line before the text wraps to the next line.

#### Images

An element of type `image` can have the following attributes:

```python
{
    "id": "example-image",
    "type": "image",
    "position": [0, 10],
    "relative_to": ["example-text", "bottom-left"],
    "anchor": "top-left",
    # Specific attributes:
    "path": "image.png",
    "filters": {
        "crop_top": 50,
        "crop_bottom": 100,
        "crop_left": -50,
        "crop_right": 10,
        "crop_box": [0, 10, 20, 10],
        "rotate": 90,
        "flip": "horizontal | vertical",
        "resize": [400, 400]
    }
}
```

Positive values in a `crop_xxxx` filter will cut rows/columns of pixels from that side of the image moving inwards, while negative values will add rows/columns of transparent pixels to that side of the image moving outwards.

#### Shapes

The following attributes are common to all shapes:

```python
{
    # Common to all elements:
    "id": "example-shape",
    "type": "circle | ellipse | ..",
    "position": [0, 0],
    "relative_to": ["<id>", "<anchor>"],
    "anchor": "top-left | center | ..",
    # Common to all shapes:
    "color": [255, 255, 255],
    "outline_color": [0, 0, 0],
    "outline_width": 2
}
```

##### Circle

The `circle` shape is defined by a center `position` and a `radius`.

```python
{
    # ...
    "position": [1000, 650],
    "radius": 200,
    # ...
}
```

##### Ellipse

The `ellipse` shape is defined by a bounding `size` box.
The ellipse will be drawn inside the box, its curve being tangent to its sides.

```python
{
    # ...
    "size": [1000, 500],
    # ...
}
```

##### Polygon

The `polygon` shape is defined by a list of `points` that will be used as vertices.

```python
{
    # ...
    "points": [[0, -100], [30, -30], [100, -30], [40, 20],
               [60, 100], [0, 50], [-60, 100], [-40, 20],
               [-100, -30], [-30, -30]],
    # ...
}
```

##### Regular polygon

The `regular-polygon` shape is constructed from a bounding circle (center `position`, `radius`),
a certain number of `sides`, and a `rotation` angle.

```python
{
    # ...
    "position": [-100, 100],
    "radius": 50,
    "sides": 6,
    "rotation": 45,
    # ...
}
```

##### Rectangle

The `rectangle` shape is described by a `size`, and can have its `corners` rounded by a given `corner_radius`.

```python
{
    # ...
    "size": [200, 300],
    "corners": [False, False, True, True]
    "corner_radius": 40,
    # ...
}
```

The `corners` attribute defines which corners should be rounded (`true`) or straight (`false`).

### Basic example with `deck.csv`

The `deck.csv` file is a semicolon-separated table with a title row and a data row for each card in the deck.

> deck.csv
```csv
name;greeting;r;g;b
John;Nice to see you again;0;255;0
Alice;Have a great day;255;0;0
```

You can reference columns from `deck.csv` in `deck.json` by their name enclosed in `%` signs.

> deck.json
```json
{
    "width": 250,
    "height": 350,
    "background_color": [180, 180, 180],
    "elements": [
        {
            "id": "name",
            "type": "text",
            "text": "Hello, %name%",
            "font_size": 24,
            "color": ["%r%", "%g%", "%b%"],
            "align": "center",
            "position": [125, 25],
            "anchor": "top-center",
        },
        {
            "id": "greeting",
            "type": "text",
            "text": "%greeting%",
            "font_size": 16,
            "color": ["%r%", "%g%", "%b%"],
            "align": "center",
            "width": 200,
            "position": [0, 25],
            "relative_to": ["name", "bottom-center"],
            "anchor": "top-center",
        }
    ]
}
```

#### Building the deck

Running `pydeck build` will create an `output` folder containing two card images, each with its own greeting in a different color.

#### Exporting to PDF

Finally, you can export the deck to PDF by running the command:

```bash
pydeck export --width 63.5 --height 88.9 --gap 0.2 output
```

The `--width` and `--height` flags define the real-world width and height in mm for each card, and the `--gap` flag adds a small line or gap between the cards, to facilitate the job of cutting them, which is especially useful for cards with no border and a similar background color.
