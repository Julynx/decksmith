"""
This module provides utility functions for text wrapping and positioning.
"""

from typing import Tuple

from PIL import ImageFont


def get_wrapped_text(text: str, font: ImageFont.ImageFont, line_length: int) -> str:
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
    wrapped_lines = []
    for line in text.split("\n"):
        lines = [""]
        for word in line.split():
            line_to_check = f"{lines[-1]} {word}".strip()
            if font.getlength(line_to_check) <= line_length:
                lines[-1] = line_to_check
            else:
                lines.append(word)
        wrapped_lines.extend(lines)
    return "\n".join(wrapped_lines)


def apply_anchor(size: Tuple[int, ...], anchor: str) -> Tuple[int, int]:
    """
    Applies an anchor to a size tuple to determine the position of an element.
    Args:
        size (Tuple[int, ...]): A tuple representing the size (width, height)
            or a bounding box (x1, y1, x2, y2).
        anchor (str): The anchor position, e.g., "center", "top-left".
    Returns:
        Tuple[int, int]: A tuple representing the position (x, y) based on the anchor.
    """
    if len(size) == (_size_box := 2):
        width, height = size
        position_horizontal, position_vertical = 0, 0
    elif len(size) == (_bounding_box := 4):
        position_horizontal, position_vertical, position_right, position_bottom = size
        width, height = (
            position_right - position_horizontal,
            position_bottom - position_vertical,
        )
    else:
        raise ValueError("Size must be a tuple of 2 or 4 integers.")

    anchor_points = {
        "top-left": (position_horizontal, position_vertical),
        "top-center": (position_horizontal + width // 2, position_vertical),
        "top-right": (position_horizontal + width, position_vertical),
        "middle-left": (position_horizontal, position_vertical + height // 2),
        "center": (
            position_horizontal + width // 2,
            position_vertical + height // 2,
        ),
        "middle-right": (position_horizontal + width, position_vertical + height // 2),
        "bottom-left": (position_horizontal, position_vertical + height),
        "bottom-center": (position_horizontal + width // 2, position_vertical + height),
        "bottom-right": (position_horizontal + width, position_vertical + height),
    }

    if anchor not in anchor_points:
        raise ValueError(f"Unknown anchor: {anchor}")

    return anchor_points[anchor]


def int_tuple(tuple_value: Tuple[any, ...]) -> Tuple[int, ...]:
    """
    Converts a tuple of any type to a tuple of integers.
    Args:
        tuple_value (Tuple[any, ...]): The tuple to convert.
    Returns:
        Tuple[int, ...]: The converted tuple.
    """
    converted = []
    for element in tuple_value:
        try:
            converted.append(int(element))
        except ValueError:
            pass
    return tuple(converted)
