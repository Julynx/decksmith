"""
This module contains logic for resolving macros in card specifications.
"""

from typing import Any, Dict


class MacroResolver:
    """
    A class to resolve macros in card specifications.
    """

    @staticmethod
    def resolve(spec: Dict[str, Any], row: Dict[str, Any]) -> Dict[str, Any]:
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
                return [replace_in_value(item) for item in value]

            if isinstance(value, dict):
                return {key: replace_in_value(item) for key, item in value.items()}

            return value

        return replace_in_value(spec)
