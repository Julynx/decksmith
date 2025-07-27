# pydeck

A command-line application to dynamically generate decks of cards from a JSON specification and a CSV data file, inspired by nandeck.

Pydeck is ideal for automating the creation of all kinds of decks, including TCG decks, tarot decks, business cards, and even slides.

## Features

Initialize a sample project and edit it instead of starting from scratch.

Include images, text, and different kinds of shapes.

Link any field to a column in the CSV file.

Position elements absolutely or relative to other elements, using anchors to simplify placement

Transform images using filters like crop, resize, rotate, or flip.

Build card images and export to PDF for printing.

## Getting started

### Installation

To begin, install pydeck by opening a Terminal and entering `pip install pydeck`.

### pydeck init

Create a new folder and run `pydeck init` inside.

This will create two different files:
- `deck.json` defines the structure for the cards in the deck. The different elements that compose a card, such as text blocks, images and shapes are declared here, along with their sizes, positions and other attributes. Edit this file with your favorite text editor to add and remove elements or modify their properties.
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

The `anchor` attribute defines the point or corner of the element that wil be used to position it within the card.
For example, declaring an element with `"position": [50, 50]` and `"anchor": "center"` means the center of the element will be in the coordinates `[50, 50]`. Using an anchor of `bottom-left` will position the bottom-left corner of the element in that position instead.

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
    "spacing": 4,
    "width": 300,
    "align": "left | center | justify | ..",
    "stroke_width": 1,
    "stroke_fill": [255, 255, 255]
}
```

The `spacing` attribute defines the vertical space in pixels between lines of text.

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
The ellipse will be drawn inside such box, its curve being tangent to all sides of the box.

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

### Referencing `deck.csv` fields


