"""
This module provides utility functions for text wrapping and positioning.
"""
from PIL import ImageFont


def get_wrapped_text(text: str, font: ImageFont.ImageFont, line_length: int):
    """
    Wraps text to fit within a specified line length using the given font.
    Args:
        text (str): The text to wrap.
        font (ImageFont.ImageFont): The font to use for measuring text length.
        line_length (int): The maximum length of each line in pixels.

    Returns:
        str: The wrapped text with newlines inserted where necessary.
    """
    lines = [""]
    for word in text.split():
        line = f"{lines[-1]} {word}".strip()
        if font.getlength(line) <= line_length:
            lines[-1] = line
        else:
            lines.append(word)
    return "\n".join(lines)


def apply_anchor(size: tuple, anchor: str):
    """
    Applies an anchor to a size tuple to determine the position of an element.
    Args:
        size (tuple): A tuple representing the size (width, height).
        anchor (str): The anchor position, e.g., "center", "top-left", 
                      "top-right", "bottom-left", "bottom-right".
    Returns:
        tuple: A tuple representing the position (x, y) based on the anchor.
    """
    x, y = size
    if anchor == "center":
        return (x // 2, y // 2)
    if anchor == "top-left":
        return (0, 0)
    if anchor == "top-right":
        return (x, 0)
    if anchor == "bottom-left":
        return (0, y)
    if anchor == "bottom-right":
        return (x, y)
    raise ValueError(f"Unknown anchor: {anchor}")
