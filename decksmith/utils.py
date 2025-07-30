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
    if len(size) == 2:
        w, h = size
        x, y = 0, 0
    elif len(size) == 4:
        x, y, x2, y2 = size
        w, h = x2 - x, y2 - y
    else:
        raise ValueError("Size must be a tuple of 2 or 4 integers.")

    anchor_points = {
        "top-left": (x, y),
        "top-center": (x + w // 2, y),
        "top-right": (x + w, y),
        "middle-left": (x, y + h // 2),
        "center": (x + w // 2, y + h // 2),
        "middle-right": (x + w, y + h // 2),
        "bottom-left": (x, y + h),
        "bottom-center": (x + w // 2, y + h),
        "bottom-right": (x + w, y + h),
    }

    if anchor not in anchor_points:
        raise ValueError(f"Unknown anchor: {anchor}")

    return anchor_points[anchor]
