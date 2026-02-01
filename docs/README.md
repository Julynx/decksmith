# DeckSmith

*A powerful application to dynamically generate decks of cards from a YAML specification and a CSV data file.*

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
- 🖥️ User-friendly GUI for easy project management and generation.
- ⚡ Highly performant card generation using parallel processing.
- 📖 Intuitive syntax and extensive [documentation](https://github.com/Julynx/decksmith/blob/main/docs/DOCS.md) with examples to help you get started.
- 🧰 Tons of powerful features such as:
  - [Start from a sample project and edit it instead of starting from scratch](https://github.com/Julynx/decksmith/blob/main/docs/DOCS.md#creating-a-project)
  - [Extensive support for images](https://github.com/Julynx/decksmith/blob/main/docs/DOCS.md#images), [text](https://github.com/Julynx/decksmith/blob/main/docs/DOCS.md#text), [and all kinds of different shapes](https://github.com/Julynx/decksmith/blob/main/docs/DOCS.md#shapes)
  - [Link any field to a column in the CSV file](https://github.com/Julynx/decksmith/blob/main/docs/DOCS.md#example-with-deckcsv)
  - [Position elements absolutely or relative to other elements, using anchors to simplify placement](https://github.com/Julynx/decksmith/blob/main/docs/DOCS.md#positioning)
  - [Powerful image transformations using filters like crop, resize, rotate, or flip](https://github.com/Julynx/decksmith/blob/main/docs/DOCS.md#images)
  - [Export your deck as images or as a PDF for printing](https://github.com/Julynx/decksmith/blob/main/docs/DOCS.md#building-the-deck)

## Getting started

### Installation

- To begin, install DeckSmith by running:

  ```bash
  pip install decksmith
  ```

- To launch the GUI, run:

  ```bash
  decksmith --gui
  ```

### Creating a project

- Run the following command to start from sample `deck.yaml` and `deck.csv` files:

  ```text
  decksmith init
  ```

  - `deck.yaml` defines the layout for the cards in the deck.
  - `deck.csv` holds the data for each card, like the content of the text fields and the image paths.

### Defining the layout

- Edit `deck.yaml` to include all the elements you want on your cards.
  You can find a complete list of all the available elements and their properties in the [documentation](https://github.com/Julynx/decksmith/blob/main/docs/DOCS.md).

- You can reference any column from `deck.csv` in the `deck.yaml` file as `%column_name%`.

### Building the deck

- When you are ready to generate the deck images, run:

  ```text
  decksmith build
  ```

- After building a deck, you can export it to PDF by running:

  ```text
  decksmith export
  ```

## Documentation

Check out the [full documentation](https://github.com/Julynx/decksmith/blob/main/docs/DOCS.md) for more detailed information on how to use DeckSmith.
