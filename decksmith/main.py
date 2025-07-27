"""
This module provides a command-line tool for building decks of cards.
"""

import os
import shutil
from importlib import resources

import traceback

import click
from decksmith.deck_builder import DeckBuilder
from decksmith.export import PdfExporter


@click.group()
def cli():
    """A command-line tool for building decks of cards."""


@cli.command()
def init():
    """Initializes a new project by creating deck.json and deck.csv."""
    if os.path.exists("deck.json") or os.path.exists("deck.csv"):
        click.echo("(!) Project already initialized.")
        return

    with resources.path("templates", "deck.json") as template_path:
        shutil.copy(template_path, "deck.json")
    with resources.path("templates", "deck.csv") as template_path:
        shutil.copy(template_path, "deck.csv")

    click.echo("(✔) Initialized new project from templates.")


@cli.command()
@click.option("--output", default="output", help="The output directory for the deck.")
@click.option(
    "--spec", default="deck.json", help="The path to the deck specification file."
)
@click.option("--data", default="deck.csv", help="The path to the data file.")
def build(output, spec, data):
    """Builds the deck of cards."""
    if not os.path.exists(output):
        os.makedirs(output)

    click.echo(f"(i) Building deck in {output}...")
    try:
        builder = DeckBuilder(spec, data)
        builder.build_deck(output)
    # pylint: disable=W0718
    except Exception as exc:
        with open("log.txt", "w", encoding="utf-8") as log:
            log.write(traceback.format_exc())
        # print(f"{traceback.format_exc()}", end="\n")
        print(f"(x) Error building deck '{data}' from spec '{spec}':")
        print(" " * 4 + f"{exc}")
        return

    click.echo("(✔) Deck built successfully.")


@cli.command()
@click.argument("image_folder")
@click.option("--output", default="output.pdf", help="The output PDF file path.")
@click.option("--page-size", default="A4", help="The page size (e.g., A4).")
@click.option(
    "--width", type=float, default=63.5, help="The width of the images in mm."
)
@click.option(
    "--height", type=float, default=88.9, help="The height of the images in mm."
)
@click.option("--gap", type=float, default=0, help="The gap between images in pixels.")
@click.option(
    "--margins",
    type=float,
    nargs=2,
    default=[2, 2],
    help="The horizontal and vertical margins in mm.",
)
def export(image_folder, output, page_size, width, height, gap, margins):
    """Exports images from a folder to a PDF file."""
    try:
        exporter = PdfExporter(
            image_folder=image_folder,
            output_path=output,
            page_size_str=page_size,
            image_width=width,
            image_height=height,
            gap=gap,
            margins=margins,
        )
        exporter.export()
        click.echo(f"(✔) Successfully exported PDF to {output}")
    # pylint: disable=W0718
    except Exception as exc:
        with open("log.txt", "w", encoding="utf-8") as log:
            log.write(traceback.format_exc())
        print(f"(x) Error exporting images to '{output}':")
        print(" " * 4 + f"{exc}")


if __name__ == "__main__":
    cli()
