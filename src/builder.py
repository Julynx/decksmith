"""
This module contains the CardBuilder class, 
which is used to create card images based on a JSON specification.
"""
import json
from PIL import Image, ImageDraw, ImageFont
from utils import get_wrapped_text


class CardBuilder:
    """
    A class to build a card image based on a JSON specification.
    Attributes:
        spec (dict): The JSON specification for the card.
        card (Image): The PIL Image object representing the card.
        draw (ImageDraw): The PIL ImageDraw object for drawing on the card.
    """
    def __init__(self, spec_path):
        """
        Initializes the CardBuilder with a JSON specification file.
        Args:
            spec_path (str): Path to the JSON specification file.
        """
        with open(spec_path, "r", encoding="utf-8") as f:
            self.spec = json.load(f)
        width = self.spec.get("width", 800)
        height = self.spec.get("height", 600)
        bg_color = tuple(self.spec.get("background_color", [255, 255, 255]))
        self.card = Image.new("RGB", (width, height), bg_color)
        self.draw = ImageDraw.Draw(self.card)

    def _draw_text(self, element:dict):
        """
        Draws text on the card based on the provided element dictionary.
        Args:
            element (dict): A dictionary containing text properties such as 
                            'text', 'font_path', 'font_size', 'position', 
                            'color', and 'width'.
        """
        assert element.pop("type") == "text", "Element type must be 'text'"

        # Convert font_path to a font object
        if font_path := element.pop("font_path", False):
            font_size = element.pop("font_size", 12)
            element["font"] = ImageFont.truetype(font_path, font_size)
        else:
            element["font"] = ImageFont.load_default()

        # Split text according to the specified width
        if line_length := element.pop("width", False):
            element["text"] = get_wrapped_text(element["text"], element["font"], line_length)

        # Convert position and color to tuples
        if position := element.pop("position", False):
            element["position"] = tuple(position)
        if color := element.pop("color", False):
            element["fill"] = tuple(color)

        # Rename color to fill
        if "color" in element:
            element["fill"] = element.pop("color")

        # Unpack the element dictionary and draw the text
        self.draw.text(element.pop("position"), element.pop("text"), **element)


    def _draw_image(self, element):
        """
        Draws an image on the card based on the provided element dictionary.
        Args:
            element (dict): A dictionary containing image properties such as 
                            'path', 'size', and 'position'.
        """
        path = element["path"]
        img = Image.open(path)
        size = element.get("size")
        if size:
            img = img.resize(tuple(size))
        position = tuple(element.get("position", [0, 0]))
        self.card.paste(img, position)

    def build(self, output_path):
        """
        Builds the card image by drawing all elements specified in the JSON.
        Args:
            output_path (str): The path where the card image will be saved.
        """
        for el in self.spec.get("elements", []):
            el_type = el["type"]
            if el_type == "text":
                self._draw_text(el)
            elif el_type == "image":
                self._draw_image(el)
            # extend with more element types here
        self.card.save(output_path)
        print(f"Card saved to {output_path}")


if __name__ == "__main__":
    builder = CardBuilder("card_spec.json")
    builder.build("output_card.png")
