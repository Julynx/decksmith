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
    expected_hash = "c66a9d5fc3f2d4efdce1453d226c83f234726464c8eb1587f01440abdde24513"

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
    expected_hash_1 = "4bf2752cd9172b187ba3bd68cf2d4d3cee8a6a660374e230e1a3f56042bade60"
    expected_hash_2 = "2863f4c45155e4ebfcf6e148a531ac6fb79eae3b97f0fa2b25aba2e073cd4203"

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
