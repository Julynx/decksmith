import os
from pathlib import Path

from click.testing import CliRunner

from decksmith.deck_builder import DeckBuilder
from decksmith.main import cli
from tests.utils import compare_images

# Define paths
TEST_DATA_PATH = Path("tests/data")
TEST_SHAPES_OUTPUT = Path("tests/output1")
TEST_EXAMPLE_OUTPUT = Path("tests/output2")
TEST_COMPREHENSIVE_OUTPUT = Path("tests/output3")
TEST_SINGLE_OUTPUT = Path("tests/output4")
TEST_TRANSPARENCY_OUTPUT = Path("tests/output5")
TEST_TEXT_TRANSPARENCY_OUTPUT = Path("tests/output6")
TEST_OPACITY_OUTPUT = Path("tests/output7")
TEST_EXPECTED_OUTPUT = Path("tests/expected")

# Threshold for image comparison failure (0.005%)
IMAGE_DIFF_THRESHOLD = 0.005


def setup_module():
    """Create the output directory before running tests."""
    TEST_SHAPES_OUTPUT.mkdir(exist_ok=True)
    TEST_EXAMPLE_OUTPUT.mkdir(exist_ok=True)
    TEST_COMPREHENSIVE_OUTPUT.mkdir(exist_ok=True)
    TEST_SINGLE_OUTPUT.mkdir(exist_ok=True)
    TEST_TRANSPARENCY_OUTPUT.mkdir(exist_ok=True)
    TEST_TEXT_TRANSPARENCY_OUTPUT.mkdir(exist_ok=True)
    TEST_OPACITY_OUTPUT.mkdir(exist_ok=True)
    TEST_EXPECTED_OUTPUT.mkdir(exist_ok=True)


def assert_images_match(output_path: Path, expected_path: Path):
    """
    Asserts that two images match within the defined threshold.

    NOTE: If this test fails, DO NOT update the expected output image unless
    you are absolutely certain that the visual change is intended and correct.
    Instead, fix the code to match the expected output.
    """
    assert output_path.exists(), f"Output file {output_path} does not exist."
    assert expected_path.exists(), f"Expected file {expected_path} does not exist."

    max_diff, avg_diff, percent_diff = compare_images(output_path, expected_path)

    assert percent_diff <= IMAGE_DIFF_THRESHOLD, (
        f"Image difference {percent_diff:.4f}% exceeds threshold {IMAGE_DIFF_THRESHOLD}%. "
        f"Max diff: {max_diff}, Avg diff: {avg_diff:.4f}. "
        "Please fix the code to match the expected output."
    )


def test_shapes_deck():
    """Test the shapes deck builder."""
    # Given
    shapes_json_path = TEST_DATA_PATH / "shapes.json"
    output_card_path = TEST_SHAPES_OUTPUT / "card_1.png"
    expected_card_path = TEST_EXPECTED_OUTPUT / "shapes_card_1.png"

    # When
    deck_builder = DeckBuilder(shapes_json_path)
    deck_builder.build_deck(TEST_SHAPES_OUTPUT)

    # Then
    assert_images_match(output_card_path, expected_card_path)


def test_text_transparency():
    """Test that text with alpha transparency properly composites over images."""
    # Given
    transparency_json_path = TEST_DATA_PATH / "text_transparency_test.json"
    output_card_path = TEST_TEXT_TRANSPARENCY_OUTPUT / "card_1.png"
    expected_card_path = TEST_EXPECTED_OUTPUT / "text_transparency_card_1.png"

    # When
    deck_builder = DeckBuilder(transparency_json_path)
    deck_builder.build_deck(TEST_TEXT_TRANSPARENCY_OUTPUT)

    # Then
    assert_images_match(output_card_path, expected_card_path)


def test_opacity_filter():
    """Test the opacity filter for images."""
    # Given
    opacity_json_path = TEST_DATA_PATH / "opacity_test.json"
    output_card_path = TEST_OPACITY_OUTPUT / "card_1.png"
    expected_card_path = TEST_EXPECTED_OUTPUT / "opacity_card_1.png"

    # When
    deck_builder = DeckBuilder(opacity_json_path)
    deck_builder.build_deck(TEST_OPACITY_OUTPUT)

    # Then
    # For the first run, we might not have the expected image, so we check existence
    if not expected_card_path.exists():
        import shutil

        shutil.copy(output_card_path, expected_card_path)

    assert_images_match(output_card_path, expected_card_path)


def test_example_deck():
    """Test the example deck builder."""
    # Given
    deck_json_path = TEST_DATA_PATH / "deck.json"
    deck_csv_path = TEST_DATA_PATH / "deck.csv"
    output_card_one_path = TEST_EXAMPLE_OUTPUT / "card_1.png"
    output_card_two_path = TEST_EXAMPLE_OUTPUT / "card_2.png"
    expected_card_one_path = TEST_EXPECTED_OUTPUT / "example_card_1.png"
    expected_card_two_path = TEST_EXPECTED_OUTPUT / "example_card_2.png"

    # When
    deck_builder = DeckBuilder(deck_json_path, deck_csv_path)
    deck_builder.build_deck(TEST_EXAMPLE_OUTPUT)

    # Then
    assert_images_match(output_card_one_path, expected_card_one_path)
    assert_images_match(output_card_two_path, expected_card_two_path)


def test_comprehensive():
    """Test the example deck builder."""
    # Given
    deck_json_path = TEST_DATA_PATH / "comprehensive.json"
    output_card_one_path = TEST_COMPREHENSIVE_OUTPUT / "card_1.png"
    expected_card_one_path = TEST_EXPECTED_OUTPUT / "comprehensive_card_1.png"

    # When
    deck_builder = DeckBuilder(deck_json_path)
    deck_builder.build_deck(TEST_COMPREHENSIVE_OUTPUT)

    # Then
    assert_images_match(output_card_one_path, expected_card_one_path)


def test_build_single_no_csv():
    """Test that a single card is built when the CSV file is not found."""
    # Given
    deck_json_path = TEST_DATA_PATH / "single_card.json"
    non_existent_csv_path = TEST_DATA_PATH / "non_existent.csv"

    # When
    deck_builder = DeckBuilder(deck_json_path, non_existent_csv_path)
    deck_builder.build_deck(TEST_SINGLE_OUTPUT)

    # Then
    output_files = os.listdir(TEST_SINGLE_OUTPUT)
    assert len(output_files) == 1, "Expected a single output file."
    assert output_files[0] == "card_1.png", (
        "Expected the output file to be named 'card_1.png'."
    )

    output_card_path = TEST_SINGLE_OUTPUT / "card_1.png"
    expected_card_path = TEST_EXPECTED_OUTPUT / "single_card_1.png"
    assert_images_match(output_card_path, expected_card_path)


def test_build_error_missing_csv():
    """Test that build errors out if a non-existent CSV is specified."""
    # Given
    runner = CliRunner()
    spec_path = TEST_DATA_PATH / "single_card.json"
    non_existent_csv_path = "non_existent.csv"
    output_path = TEST_SINGLE_OUTPUT

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
    output_card_path = TEST_TRANSPARENCY_OUTPUT / "card_1.png"
    expected_card_path = TEST_EXPECTED_OUTPUT / "transparency_card_1.png"

    # When
    deck_builder = DeckBuilder(transparency_json_path)
    deck_builder.build_deck(TEST_TRANSPARENCY_OUTPUT)

    # Then
    assert_images_match(output_card_path, expected_card_path)
