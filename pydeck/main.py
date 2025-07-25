"""
This module provides a command-line tool for building decks of cards.
"""

import os
import shutil
from importlib import resources

import click
from pydeck.deck_builder import DeckBuilder


@click.group()
def cli():
    """A command-line tool for building decks of cards."""


@cli.command()
def init():
    """Initializes a new project by creating deck.json and deck.csv."""
    if os.path.exists("deck.json") or os.path.exists("deck.csv"):
        click.echo("Project already initialized.")
        return

    with resources.path("templates", "deck.json") as template_path:
        shutil.copy(template_path, "deck.json")
    with resources.path("templates", "deck.csv") as template_path:
        shutil.copy(template_path, "deck.csv")

    click.echo("Initialized new project from templates.")


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

    click.echo(f"Building deck in {output}...")
    builder = DeckBuilder(spec, data)
    builder.build_deck(output)
    click.echo("Deck built successfully.")


if __name__ == "__main__":
    cli()
