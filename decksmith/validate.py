"""
Python module for validating a dictionar
"""

from jval import validate

ELEMENT_SPEC = {
    "?*id": "<str>",
    "*type": "<str>",
    "?*position": ["<float>"],
    "?*relative_to": ["<str>"],
    "?*anchor": "<str>",
}

SPECS_FOR_TYPE = {
    "text": {
        "*text": "<str>",
        "?*color": ["<int>"],
        "?*font_path": "<str>",
        "?*font_size": "<int>",
        "?*font_variant": "<str>",
        "?*line_spacing": "<int>",
        "?*width": "<int>",
        "?*align": "<str>",
        "?*stroke_width": "<int>",
        "?*stroke_color": ["<int>"],
    },
    "image": {
        "*path": "<str>",
        "?*filters": {
            "?*crop_top": "<int>",
            "?*crop_bottom": "<int>",
            "?*crop_left": "<int>",
            "?*crop_right": "<int>",
            "?*crop_box": ["<int>"],
            "?*rotate": "<int>",
            "?*flip": "<str>",
            "?*resize": ["<?int>"],
        },
    },
    "circle": {
        "*radius": "<int>",
        "?*color": ["<int>"],
        "?*outline_color": ["<int>"],
        "?*outline_width": "<int>",
    },
    "ellipse": {
        "*size": ["<int>"],
        "?*color": ["<int>"],
        "?*outline_color": ["<int>"],
        "?*outline_width": "<int>",
    },
    "polygon": {
        "*points": [["<int>"]],
        "?*color": ["<int>"],
        "?*outline_color": ["<int>"],
        "?*outline_width": "<int>",
    },
    "regular-polygon": {
        "*radius": "<int>",
        "*sides": "<int>",
        "?*rotation": "<int>",
        "?*color": ["<int>"],
        "?*outline_color": ["<int>"],
        "?*outline_width": "<int>",
    },
    "rectangle": {
        "*size": ["<int>"],
        "?*corners": ["<bool>"],
        "?*corner_radius": "<int>",
        "?*color": ["<int>"],
        "?*outline_color": ["<int>"],
        "?*outline_width": "<int>",
    },
}

CARD_SPEC = {
    "*width": "<int>",
    "*height": "<int>",
    "?*background_color": ["<int>"],
    "*elements": [],
}


def validate_element(element, element_type):
    """
    Validates an element of a card against a spec, raising an exception
    if it does not meet the spec.
    Args:
        element (dict): The card element.
        element_type (str): The type of the element
    """
    spec = ELEMENT_SPEC | SPECS_FOR_TYPE[element_type]
    validate(element, spec)


def validate_card(card):
    """
    Validates a card against a spec, raising an exception
    if it does not meet the spec.
    Args:
        card (dict): The card.
    """
    # print(f"DEBUG:\n{card=}")
    validate(card, CARD_SPEC)
    for element in card["elements"]:
        # print(f"DEBUG: {element['type']}")
        validate_element(element, element["type"])
