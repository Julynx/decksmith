import hashlib
import os
from pathlib import Path

from click.testing import CliRunner
from decksmith.main import cli
from decksmith.deck_builder import DeckBuilder

# Define paths
TEST_DATA_PATH = Path("test/data")
TEST_1_OUTPUT_PATH = Path("test/output1")
TEST_2_OUTPUT_PATH = Path("test/output2")
TEST_3_OUTPUT_PATH = Path("test/output3")
TEST_4_OUTPUT_PATH = Path("test/output4")
TEST_5_OUTPUT_PATH = Path("test/output5")


def setup_module():
    """Create the output directory before running tests."""
    TEST_1_OUTPUT_PATH.mkdir(exist_ok=True)
    TEST_2_OUTPUT_PATH.mkdir(exist_ok=True)
    TEST_3_OUTPUT_PATH.mkdir(exist_ok=True)
    TEST_4_OUTPUT_PATH.mkdir(exist_ok=True)
    TEST_5_OUTPUT_PATH.mkdir(exist_ok=True)


def test_shapes_deck():
    """Test the shapes deck builder."""
    # Given
    shapes_json_path = TEST_DATA_PATH / "shapes.json"
    output_card_path = TEST_1_OUTPUT_PATH / "card_1.png"
    expected_hash = "c66a9d5fc3f2d4efdce1453d226c83f234726464c8eb1587f01440abdde24513"

    # When
    deck_builder = DeckBuilder(shapes_json_path)
    deck_builder.build_deck(TEST_1_OUTPUT_PATH)

    # Then
    with open(output_card_path, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()

    assert (
        file_hash == expected_hash
    ), "The output file hash does not match the expected value."


def test_example_deck():
    """Test the example deck builder."""
    # Given
    deck_json_path = TEST_DATA_PATH / "deck.json"
    deck_csv_path = TEST_DATA_PATH / "deck.csv"
    output_card_1_path = TEST_2_OUTPUT_PATH / "card_1.png"
    output_card_2_path = TEST_2_OUTPUT_PATH / "card_2.png"
    expected_hash_1 = "4bf2752cd9172b187ba3bd68cf2d4d3cee8a6a660374e230e1a3f56042bade60"
    expected_hash_2 = "2863f4c45155e4ebfcf6e148a531ac6fb79eae3b97f0fa2b25aba2e073cd4203"

    # When
    deck_builder = DeckBuilder(deck_json_path, deck_csv_path)
    deck_builder.build_deck(TEST_2_OUTPUT_PATH)

    # Then
    with open(output_card_1_path, "rb") as f:
        file_hash_1 = hashlib.sha256(f.read()).hexdigest()
    assert (
        file_hash_1 == expected_hash_1
    ), "The output file hash does not match the expected value."

    with open(output_card_2_path, "rb") as f:
        file_hash_2 = hashlib.sha256(f.read()).hexdigest()
    assert (
        file_hash_2 == expected_hash_2
    ), "The output file hash does not match the expected value."


def test_comprehensive():
    """Test the example deck builder."""
    # Given
    deck_json_path = TEST_DATA_PATH / "comprehensive.json"
    output_card_1_path = TEST_3_OUTPUT_PATH / "card_1.png"
    expected_hash_1 = "760f88e6206971b28668ced5ae7f52cfbcfea5e601fa252af58d6d479300b08b"

    # When
    deck_builder = DeckBuilder(deck_json_path)
    deck_builder.build_deck(TEST_3_OUTPUT_PATH)

    # Then
    with open(output_card_1_path, "rb") as f:
        file_hash_1 = hashlib.sha256(f.read()).hexdigest()
    assert (
        file_hash_1 == expected_hash_1
    ), "The output file hash does not match the expected value."


def test_build_single_card_when_csv_not_found():
    """Test that a single card is built when the CSV file is not found."""
    # Given
    deck_json_path = TEST_DATA_PATH / "single_card.json"
    non_existent_csv_path = TEST_DATA_PATH / "non_existent.csv"

    # When
    deck_builder = DeckBuilder(deck_json_path, non_existent_csv_path)
    deck_builder.build_deck(TEST_4_OUTPUT_PATH)

    # Then
    output_files = os.listdir(TEST_4_OUTPUT_PATH)
    assert len(output_files) == 1, "Expected a single output file."
    assert (
        output_files[0] == "card_1.png"
    ), "Expected the output file to be named 'card_1.png'."


def test_build_errors_on_explicit_missing_csv():
    """Test that build errors out if a non-existent CSV is specified."""
    # Given
    runner = CliRunner()
    spec_path = TEST_DATA_PATH / "single_card.json"
    non_existent_csv_path = "non_existent.csv"
    output_path = TEST_4_OUTPUT_PATH

    # When
    result = runner.invoke(
        cli,
        [
            "build",
            "--spec",
            str(spec_path),
            "--data",
            non_existent_csv_path,
            "--output",
            str(output_path),
        ],
    )

    # Then
    assert result.exit_code != 0
    assert f"Data file not found: {non_existent_csv_path}" in result.output


def test_transparency():
    """Test that rectangles with alpha transparency properly composite over images."""
    # Given
    transparency_json_path = TEST_DATA_PATH / "transparency_test.json"
    output_card_path = TEST_5_OUTPUT_PATH / "card_1.png"
    expected_hash = "36ed25e7962742bfd742ae6b97aa783d226fd8b9f74c6f0b75c3fc2e6c6b2fb7"

    # When
    deck_builder = DeckBuilder(transparency_json_path)
    deck_builder.build_deck(TEST_5_OUTPUT_PATH)

    # Then
    with open(output_card_path, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()

    assert (
        file_hash == expected_hash
    ), "The output file hash does not match the expected value."
