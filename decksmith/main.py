"""
This module provides a command-line tool for building decks of cards.
"""

import shutil
import traceback
from importlib import resources
from pathlib import Path

import click

from decksmith.deck_builder import DeckBuilder
from decksmith.export import PdfExporter
from decksmith.gui.app import main as gui_main
from decksmith.logger import logger


@click.group(invoke_without_command=True)
@click.option("--gui", is_flag=True, help="Launch the graphical user interface.")
@click.pass_context
def cli(ctx, gui):
    """A command-line tool for building decks of cards."""
    if gui:
        gui_main()
    elif ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
def init():
    """Initializes a new project by creating deck.yaml and deck.csv."""
    if Path("deck.yaml").exists() or Path("deck.csv").exists():
        click.echo("(!) Project already initialized.")
        return

    with resources.path("decksmith.templates", "deck.yaml") as template_path:
        shutil.copy(template_path, "deck.yaml")
    with resources.path("decksmith.templates", "deck.csv") as template_path:
        shutil.copy(template_path, "deck.csv")

    click.echo("(✔) Initialized new project from templates.")


@cli.command(context_settings={"show_default": True})
@click.option("--output", default="output", help="The output directory for the deck.")
@click.option(
    "--spec", default="deck.yaml", help="The path to the deck specification file."
)
@click.option("--data", default="deck.csv", help="The path to the data file.")
@click.pass_context
def build(ctx, output, spec, data):
    """Builds the deck of cards."""
    output_path = Path(output)
    output_path.mkdir(exist_ok=True)

    logger.info("(i) Building deck in %s...", output_path)

    try:
        spec_path = Path(spec)
        if not spec_path.exists():
            raise FileNotFoundError(f"Spec file not found: {spec_path}")

        csv_path = Path(data)
        if not csv_path.exists():
            source = ctx.get_parameter_source("data")
            if source.name == "DEFAULT":
                logger.info(
                    "(i) Building a single card deck because '%s' was not found",
                    csv_path,
                )
                csv_path = None
            else:
                raise FileNotFoundError(f"Data file not found: {csv_path}")

        builder = DeckBuilder(spec_path, csv_path)
        builder.build_deck(output_path)
    except FileNotFoundError as exc:
        click.echo(f"(x) {exc}")
        ctx.exit(1)
    # pylint: disable=W0718
    except Exception as exc:
        logger.error("(x) Error building deck '%s' from spec '%s':", data, spec)
        logger.error("    %s\n%s", exc, traceback.format_exc())
        ctx.exit(1)

    logger.info("(✔) Deck built successfully.")


@cli.command(context_settings={"show_default": True})
@click.argument("image_folder")
@click.option(
    "--output", default="output.pdf", help="The path for the output PDF file."
)
@click.option(
    "--page-size", default="A4", help="The page size for the PDF (e.g., A4, Letter)."
)
@click.option(
    "--width", type=float, default=63.5, help="The width for each image in millimeters."
)
@click.option(
    "--height",
    type=float,
    default=88.9,
    help="The height for each image in millimeters.",
)
@click.option(
    "--gap", type=float, default=0, help="The gap between images in millimeters."
)
@click.option(
    "--margins",
    type=float,
    nargs=2,
    default=[2, 2],
    help="The horizontal and vertical page margins in millimeters.",
)
@click.pass_context
def export(ctx, image_folder, output, page_size, width, height, gap, margins):
    """Exports images from a folder to a PDF file."""
    try:
        image_folder_path = Path(image_folder)
        if not image_folder_path.exists():
            raise FileNotFoundError(f"Image folder not found: {image_folder_path}")

        exporter = PdfExporter(
            image_folder=image_folder_path,
            output_path=Path(output),
            page_size_str=page_size,
            image_width=width,
            image_height=height,
            gap=gap,
            margins=margins,
        )
        exporter.export()
        logger.info("(✔) Successfully exported PDF to %s", output)
    except FileNotFoundError as exc:
        click.echo(f"(x) {exc}")
        ctx.exit(1)
    # pylint: disable=W0718
    except Exception as exc:
        logger.error("(x) Error exporting images to '%s':", output)
        logger.error("    %s\n%s", exc, traceback.format_exc())
        ctx.exit(1)


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    cli()
