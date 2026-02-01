"""
This module provides functions for validating and transforming card specifications.
"""

from typing import Any, Dict

import pandas as pd
from jval import validate

ELEMENT_SPEC: Dict[str, Any] = {
    "?*id": "<?str>",
    "*type": "<?str>",
    "?*position": ["<?float>"],
    "?*relative_to": ["<?str>"],
    "?*anchor": "<?str>",
}

SPECS_FOR_TYPE: Dict[str, Dict[str, Any]] = {
    "text": {
        "*text": "<?str>",
        "?*color": ["<?int>"],
        "?*font_path": "<?str>",
        "?*font_size": "<?int>",
        "?*font_variant": "<?str>",
        "?*line_spacing": "<?int>",
        "?*width": "<?int>",
        "?*align": "<?str>",
        "?*stroke_width": "<?int>",
        "?*stroke_color": ["<?int>"],
    },
    "image": {
        "*path": "<?str>",
        "?*filters": {
            "?*crop_top": "<?int>",
            "?*crop_bottom": "<?int>",
            "?*crop_left": "<?int>",
            "?*crop_right": "<?int>",
            "?*crop_box": ["<?int>"],
            "?*rotate": "<?int>",
            "?*flip": "<?str>",
            "?*resize": ["<?int>"],
        },
    },
    "circle": {
        "*radius": "<?int>",
        "?*color": ["<?int>"],
        "?*outline_color": ["<?int>"],
        "?*outline_width": "<?int>",
    },
    "ellipse": {
        "*size": ["<?int>"],
        "?*color": ["<?int>"],
        "?*outline_color": ["<?int>"],
        "?*outline_width": "<?int>",
    },
    "polygon": {
        "*points": [["<?int>"]],
        "?*color": ["<?int>"],
        "?*outline_color": ["<?int>"],
        "?*outline_width": "<?int>",
    },
    "regular-polygon": {
        "*radius": "<?int>",
        "*sides": "<?int>",
        "?*rotation": "<?int>",
        "?*color": ["<?int>"],
        "?*outline_color": ["<?int>"],
        "?*outline_width": "<?int>",
    },
    "rectangle": {
        "*size": ["<?int>"],
        "?*corners": ["<?bool>"],
        "?*corner_radius": "<?int>",
        "?*color": ["<?int>"],
        "?*outline_color": ["<?int>"],
        "?*outline_width": "<?int>",
    },
}

CARD_SPEC: Dict[str, Any] = {
    "?*id": "<?str>",
    "*width": "<?int>",
    "*height": "<?int>",
    "?*background_color": ["<?int>"],
    "*elements": [],
}


def validate_element(element: Dict[str, Any], element_type: str):
    """
    Validates an element of a card against a spec, raising an exception
    if it does not meet the spec.
    Args:
        element (dict): The card element.
        element_type (str): The type of the element
    """
    spec = ELEMENT_SPEC | SPECS_FOR_TYPE[element_type]
    validate(element, spec)


def validate_card(card: Dict[str, Any]):
    """
    Validates a card against a spec, raising an exception
    if it does not meet the spec.
    Args:
        card (Dict[str, Any]): The card.
    """
    # print(f"DEBUG:\n{card=}")
    validate(card, CARD_SPEC)
    for element in card["elements"]:
        # print(f"DEBUG: {element['type']}")
        validate_element(element, element["type"])


def transform_card(card: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform certain automatic type casts on the card and its
    elements. For example, cast the "text" property of elements
    of type "text" to str, to support painting numbers as text.
    Args:
        card (Dict[str, Any]): The card.
    Return:
        Dict[str, Any]: The transformed card with all automatic casts applied.
    """
    for element in card.get("elements", []):
        if element.get("type") == "text" and "text" in element:
            if pd.isna(element["text"]):
                element["text"] = None
            else:
                element["text"] = str(element["text"])

    return card
