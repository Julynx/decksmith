"""
This module contains image processing operations (filters) used by CardBuilder.
"""

from typing import Any, Dict, List, Tuple

from PIL import Image


class ImageOps:
    """
    A class to handle image processing operations.
    """

    @staticmethod
    def apply_filters(img: Image.Image, filters: Dict[str, Any]) -> Image.Image:
        """
        Applies a set of filters to an image.
        Args:
            img (Image.Image): The image to process.
            filters (Dict[str, Any]): A dictionary of filters to apply.
        Returns:
            Image.Image: The processed image.
        """
        for filter_name, filter_value in filters.items():
            filter_method_name = f"_filter_{filter_name}"
            if hasattr(ImageOps, filter_method_name):
                filter_method = getattr(ImageOps, filter_method_name)
                img = filter_method(img, filter_value)
        return img

    @staticmethod
    def _filter_crop(img: Image.Image, crop_values: List[int]) -> Image.Image:
        return img.crop(tuple(crop_values))

    @staticmethod
    def _filter_crop_top(img: Image.Image, value: int) -> Image.Image:
        if value < 0:
            img = img.convert("RGBA")
            new_img = Image.new("RGBA", (img.width, img.height - value), (0, 0, 0, 0))
            new_img.paste(img, (0, -value))
            return new_img
        return img.crop((0, value, img.width, img.height))

    @staticmethod
    def _filter_crop_bottom(img: Image.Image, value: int) -> Image.Image:
        if value < 0:
            img = img.convert("RGBA")
            new_img = Image.new("RGBA", (img.width, img.height - value), (0, 0, 0, 0))
            new_img.paste(img, (0, 0))
            return new_img
        return img.crop((0, 0, img.width, img.height - value))

    @staticmethod
    def _filter_crop_left(img: Image.Image, value: int) -> Image.Image:
        if value < 0:
            img = img.convert("RGBA")
            new_img = Image.new("RGBA", (img.width - value, img.height), (0, 0, 0, 0))
            new_img.paste(img, (-value, 0))
            return new_img
        return img.crop((value, 0, img.width, img.height))

    @staticmethod
    def _filter_crop_right(img: Image.Image, value: int) -> Image.Image:
        if value < 0:
            img = img.convert("RGBA")
            new_img = Image.new("RGBA", (img.width - value, img.height), (0, 0, 0, 0))
            new_img.paste(img, (0, 0))
            return new_img
        return img.crop((0, 0, img.width - value, img.height))

    @staticmethod
    def _filter_crop_box(img: Image.Image, box: List[int]) -> Image.Image:
        img = img.convert("RGBA")
        position_horizontal, position_vertical, width, height = box
        new_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        source_left = max(0, position_horizontal)
        source_top = max(0, position_vertical)
        source_right = min(img.width, position_horizontal + width)
        source_bottom = min(img.height, position_vertical + height)
        if source_left < source_right and source_top < source_bottom:
            source_width = source_right - source_left
            source_height = source_bottom - source_top
            src_img = img.crop(
                (
                    source_left,
                    source_top,
                    source_left + source_width,
                    source_top + source_height,
                )
            )
            destination_horizontal = source_left - position_horizontal
            destination_vertical = source_top - position_vertical
            new_img.paste(src_img, (destination_horizontal, destination_vertical))
        return new_img

    @staticmethod
    def _filter_resize(img: Image.Image, size: Tuple[int, int]) -> Image.Image:
        new_width, new_height = size
        if new_width is None and new_height is None:
            return img
        if new_width is None or new_height is None:
            original_width, original_height = img.size
            aspect_ratio = original_width / float(original_height)
            if new_width is None:
                new_width = int(new_height * aspect_ratio)
            else:
                new_height = int(new_width / aspect_ratio)
        return img.resize((new_width, new_height))

    @staticmethod
    def _filter_rotate(img: Image.Image, angle: float) -> Image.Image:
        return img.rotate(angle, expand=True)

    @staticmethod
    def _filter_flip(img: Image.Image, direction: str) -> Image.Image:
        if direction == "horizontal":
            return img.transpose(Image.FLIP_LEFT_RIGHT)
        if direction == "vertical":
            return img.transpose(Image.FLIP_TOP_BOTTOM)
        return img
