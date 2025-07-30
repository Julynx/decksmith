"""
This module contains the DeckBuilder class,
which is used to create a deck of cards based on a JSON specification
and a CSV file.
"""

import concurrent.futures
import json
from pathlib import Path
from typing import Union, List, Dict, Any

import pandas as pd
from pandas import Series

from .card_builder import CardBuilder


class DeckBuilder:
    """
    A class to build a deck of cards based on a JSON specification and a CSV file.
    Attributes:
        spec_path (Path): Path to the JSON specification file.
        csv_path (Union[Path, None]): Path to the CSV file containing card data.
        cards (list): List of CardBuilder instances for each card in the deck.
    """

    def __init__(self, spec_path: Path, csv_path: Union[Path, None] = None):
        """
        Initializes the DeckBuilder with a JSON specification file and a CSV file.
        Args:
            spec_path (Path): Path to the JSON specification file.
            csv_path (Union[Path, None]): Path to the CSV file containing card data.
        """
        self.spec_path = spec_path
        self.csv_path = csv_path
        self.cards: List[CardBuilder] = []

    def _replace_macros(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Replaces %colname% macros in the card specification with values from the row.
        Works recursively for nested structures.
        Args:
            row (dict): A dictionary representing a row from the CSV file.
        Returns:
            dict: The updated card specification with macros replaced.
        """

        def replace_in_value(value: Any) -> Any:
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

    def build_deck(self, output_path: Path):
        """
        Builds the deck of cards by reading the CSV file and creating CardBuilder instances.
        """
        if not self.csv_path or not self.csv_path.exists():
            with open(self.spec_path, "r", encoding="utf-8") as f:
                spec = json.load(f)
            card_builder = CardBuilder(spec)
            card_builder.build(output_path / "card_1.png")
            return

        df = pd.read_csv(self.csv_path, encoding="utf-8", sep=";", header=0)

        def build_card(row_tuple: tuple[int, Series]):
            """
            Builds a single card from a row of the CSV file.
            Args:
                row_tuple (tuple[int, Series]): A tuple containing the row index and the row data.
            """
            idx, row = row_tuple
            spec = self._replace_macros(row.to_dict())
            card_builder = CardBuilder(spec)
            card_builder.build(output_path / f"card_{idx + 1}.png")

        with concurrent.futures.ThreadPoolExecutor() as executor:
            list(executor.map(build_card, df.iterrows()))

        # for row_tuple in df.iterrows():
        #     build_card(row_tuple)
