# DeckSmith

*A command-line application to dynamically generate decks of cards from a JSON specification and a CSV data file, inspired by nandeck.*

<br>
<p align="center">
  <img width="600" src="https://raw.githubusercontent.com/Julynx/decksmith/refs/heads/main/docs/assets/decksmith.png">
</p>

<br>
<p align="center">
  <img width="600" src="https://raw.githubusercontent.com/Julynx/decksmith/refs/heads/main/docs/assets/banner.png">
</p>

<br>

DeckSmith is ideal for automating the creation of all kinds of decks, including TCG decks, tarot decks, business cards, and even slides.

## Why DeckSmith?

- ✨ Consistent layout and formatting across all cards. Define once, edit anytime, generate as many cards as you need.
- 🍳 Pure python, with easy installation via pip.
- ⚡ Highly performant card generation using parallel processing.
- 📖 Intuitive syntax and extensive [documentation](https://github.com/Julynx/decksmith/blob/main/docs/DOCS.md) with examples to help you get started quickly.
- 🧰 Tons of powerful features such as:
  - [Start from a sample project and edit it instead of starting from scratch](https://github.com/Julynx/decksmith/blob/main/docs/DOCS.md#creating-a-project)
  - [Extensive support for images](https://github.com/Julynx/decksmith/blob/main/docs/DOCS.md#images), [text](https://github.com/Julynx/decksmith/blob/main/docs/DOCS.md#text), [and all kinds of different shapes](https://github.com/Julynx/decksmith/blob/main/docs/DOCS.md#shapes)
  - [Link any field to a column in the CSV file](https://github.com/Julynx/decksmith/blob/main/docs/DOCS.md#basic-example-with-deckcsv)
  - [Position elements absolutely or relative to other elements, using anchors to simplify placement](https://github.com/Julynx/decksmith/blob/main/docs/DOCS.md#positioning)
  - [Powerful image transformations using filters like crop, resize, rotate, or flip](https://github.com/Julynx/decksmith/blob/main/docs/DOCS.md#images)
  - [Export your deck as images or as a PDF for printing](https://github.com/Julynx/decksmith/blob/main/docs/DOCS.md#building-the-deck)

## Getting started

- First, install DeckSmith by running `pip install decksmith`.

- Then, run `decksmith init` to start from sample `deck.json` and `deck.csv` files.

- The `deck.json` file defines the layout for the cards in the deck, while the `deck.csv` file holds the data for each card.

  - You can find a complete list of all the available elements you can use in the [documentation](https://github.com/Julynx/decksmith/blob/main/docs/DOCS.md).

  - Any column from the CSV can be referenced anywhere in the JSON as `%column_name%`.

- Finally, run `decksmith build` when you are ready to generate the deck images, and export them to PDF using the `decksmith export` command.

## Documentation

Check out the [full documentation](https://github.com/Julynx/decksmith/blob/main/docs/DOCS.md) for more detailed information on how to use DeckSmith.
