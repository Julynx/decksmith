"""
This module contains the DeckBuilder class,
which is used to create a deck of cards based on a JSON specification
and a CSV file.
"""

import concurrent.futures
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from pandas import Series
from ruamel.yaml import YAML

from decksmith.card_builder import CardBuilder
from decksmith.logger import logger


class DeckBuilder:
    """
    A class to build a deck of cards based on a JSON specification and a CSV file.
    Attributes:
        spec_path (Path): Path to the JSON specification file.
        csv_path (Union[Path, None]): Path to the CSV file containing card data.
        cards (list): List of CardBuilder instances for each card in the deck.
    """

    def __init__(self, spec_path: Path, csv_path: Optional[Path] = None):
        """
        Initializes the DeckBuilder with a JSON specification file and a CSV file.
        Args:
            spec_path (Path): Path to the JSON specification file.
            csv_path (Union[Path, None]): Path to the CSV file containing card data.
        """
        self.spec_path = spec_path
        self.csv_path = csv_path
        self.cards: List[CardBuilder] = []
        self._spec_cache: Optional[Dict[str, Any]] = None

    @property
    def spec(self) -> Dict[str, Any]:
        """Loads and caches the spec file."""
        if self._spec_cache is None:
            yaml = YAML()
            with open(self.spec_path, "r", encoding="utf-8") as f:
                self._spec_cache = yaml.load(f)
        return self._spec_cache

    @staticmethod
    def resolve_macros(spec: Dict[str, Any], row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Replaces %colname% macros in the card specification with values from the row.
        Works recursively for nested structures.
        Args:
            spec (dict): The card specification.
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

        return replace_in_value(spec)

    def build_deck(self, output_path: Path):
        """
        Builds the deck of cards by reading the CSV file and creating CardBuilder instances.
        """
        base_path = self.spec_path.parent if self.spec_path else None

        if not self.csv_path or not self.csv_path.exists():
            logger.info("No CSV file found. Building single card from spec.")
            card_builder = CardBuilder(self.spec, base_path=base_path)
            card_builder.build(output_path / "card_1.png")
            return

        try:
            df = pd.read_csv(self.csv_path, encoding="utf-8", sep=";", header=0)
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            return

        def build_card(row_tuple: tuple[int, Series]):
            """
            Builds a single card from a row of the CSV file.
            Args:
                row_tuple (tuple[int, Series]): A tuple containing the row index and the row data.
            """
            idx, row = row_tuple
            try:
                # We need a deep copy of the spec for each card to avoid side effects
                # But resolve_macros creates a new structure, so it should be fine
                spec = self.resolve_macros(self.spec, row.to_dict())
                card_builder = CardBuilder(spec, base_path=base_path)
                card_builder.build(output_path / f"card_{idx + 1}.png")
            except Exception as e:
                logger.error(f"Error building card {idx + 1}: {e}")

        with concurrent.futures.ThreadPoolExecutor() as executor:
            list(executor.map(build_card, df.iterrows()))
