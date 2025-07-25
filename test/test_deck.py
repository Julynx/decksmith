import hashlib
import os
from pathlib import Path

from pydeck.deck_builder import DeckBuilder

# Define paths
TEST_DATA_PATH = Path("test/data")
TEST_OUTPUT_PATH = Path("test/output")


def setup_module():
    """Create the output directory before running tests."""
    TEST_OUTPUT_PATH.mkdir(exist_ok=True)


def test_shapes_deck():
    """Test the shapes deck builder."""
    # Given
    shapes_json_path = TEST_DATA_PATH / "shapes.json"
    output_card_path = TEST_OUTPUT_PATH / "card_1.png"
    expected_hash = "54da15e2ff079563f919f95cbc0236d72b4ba7669520a1ec2c1fd01a835ee7be"

    # When
    deck_builder = DeckBuilder(shapes_json_path)
    deck_builder.build_deck(TEST_OUTPUT_PATH)

    # Then
    with open(output_card_path, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()

    assert file_hash == expected_hash, "The output file hash does not match the expected value."


def test_example_deck():
    """Test the example deck builder."""
    # Given
    deck_json_path = TEST_DATA_PATH / "deck.json"
    deck_csv_path = TEST_DATA_PATH / "deck.csv"
    output_card_1_path = TEST_OUTPUT_PATH / "card_1.png"
    output_card_2_path = TEST_OUTPUT_PATH / "card_2.png"
    expected_hash_1 = "cf37526ff2cefc15060e1daa63450148bb42fc997d5ae141093562fb2d6857e8"
    expected_hash_2 = "24480d94916b9e8574f65334032598ae830e1eb64abd70ca219301f4c6bece8a"

    # When
    deck_builder = DeckBuilder(deck_json_path, deck_csv_path)
    deck_builder.build_deck(TEST_OUTPUT_PATH)

    # Then
    with open(output_card_1_path, "rb") as f:
        file_hash_1 = hashlib.sha256(f.read()).hexdigest()
    assert file_hash_1 == expected_hash_1, "The output file hash does not match the expected value."

    with open(output_card_2_path, "rb") as f:
        file_hash_2 = hashlib.sha256(f.read()).hexdigest()
    assert file_hash_2 == expected_hash_2, "The output file hash does not match the expected value."
