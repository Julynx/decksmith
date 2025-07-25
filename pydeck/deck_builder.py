"""
This module contains the DeckBuilder class,
which is used to create a deck of cards based on a JSON specification
and a CSV file.
"""

import json
from pathlib import Path
import pandas as pd
from .card_builder import CardBuilder


class DeckBuilder:
    """
    A class to build a deck of cards based on a JSON specification and a CSV file.
    Attributes:
        spec_path (str): Path to the JSON specification file.
        csv_path (str): Path to the CSV file containing card data.
        cards (list): List of CardBuilder instances for each card in the deck.
    """

    def __init__(self, spec_path: str, csv_path: str):
        """
        Initializes the DeckBuilder with a JSON specification file and a CSV file.
        Args:
            spec_path (str): Path to the JSON specification file.
            csv_path (str): Path to the CSV file containing card data.
        """
        self.spec_path = spec_path
        self.csv_path = csv_path
        self.cards = []

    def _replace_macros(self, row: dict) -> dict:
        """
        Replaces %colname% macros in the card specification with values from the row.
        Works recursively for nested structures.
        Args:
            row (dict): A dictionary representing a row from the CSV file.
        Returns:
            dict: The updated card specification with macros replaced.
        """

        def replace_in_value(value):
            if isinstance(value, str):
                stripped_value = value.strip()
                # First, check for an exact macro match to preserve type
                for key in row:
                    if stripped_value == f"%{key}%":
                        return row[key]  # Return the raw value, preserving type

                # If no exact match, perform standard string replacement for all macros
                for key, val in row.items():
                    value = value.replace(f"%{key}%", str(val))
                return value

            if isinstance(value, list):
                return [replace_in_value(v) for v in value]

            if isinstance(value, dict):
                return {k: replace_in_value(v) for k, v in value.items()}

            return value

        with open(self.spec_path, "r", encoding="utf-8") as f:
            spec = json.load(f)
        return replace_in_value(spec)

    def build_deck(self, output_path: str):
        """
        Builds the deck of cards by reading the CSV file and creating CardBuilder instances.
        """
        df = pd.read_csv(self.csv_path, encoding="utf-8", sep=";", header=0)
        for idx, row in df.iterrows():
            spec = self._replace_macros(row.to_dict())
            card_builder = CardBuilder(spec)
            card_builder.build(Path(output_path) / f"card_{idx + 1}.png")
