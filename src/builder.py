import json
from PIL import Image, ImageDraw, ImageFont
from .utils import get_wrapped_text


class CardBuilder:
    def __init__(self, spec_path):
        with open(spec_path, "r") as f:
            self.spec = json.load(f)
        width = self.spec.get("width", 800)
        height = self.spec.get("height", 600)
        bg_color = tuple(self.spec.get("background_color", [255, 255, 255]))
        self.card = Image.new("RGB", (width, height), bg_color)
        self.draw = ImageDraw.Draw(self.card)

    def _draw_text(self, element:dict):
        assert element.pop("type") == "text", "Element type must be 'text'"

        # Convert font_path to a font object
        if font_path := element.pop("font_path", False):
            element["font"] = ImageFont.truetype(font_path, element.pop("font_size", 12))
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
        path = element["path"]
        img = Image.open(path)
        size = element.get("size")
        if size:
            img = img.resize(tuple(size))
        position = tuple(element.get("position", [0, 0]))
        self.card.paste(img, position)

    def build(self, output_path):
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
