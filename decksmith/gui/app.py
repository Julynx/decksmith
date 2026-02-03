"""
This module contains the Flask application for the DeckSmith GUI.
"""

import io
import json
import os
import signal
import threading
import time
import traceback
import webbrowser
from io import StringIO
from pathlib import Path
from threading import Timer

import pandas as pd
from flask import (
    Flask,
    Response,
    jsonify,
    render_template,
    request,
    send_file,
    stream_with_context,
)
from platformdirs import user_documents_dir
from ruamel.yaml import YAML
from waitress import serve

from decksmith.card_builder import CardBuilder
from decksmith.deck_builder import DeckBuilder
from decksmith.export import PdfExporter
from decksmith.logger import logger
from decksmith.macro import MacroResolver
from decksmith.project import ProjectManager

app = Flask(__name__)

shutdown_event = threading.Event()
SHUTDOWN_REASON = "Server stopped."


def signal_handler(sig, frame):  # pylint: disable=unused-argument
    """Handles system signals (e.g., SIGINT)."""
    global SHUTDOWN_REASON  # pylint: disable=global-statement
    SHUTDOWN_REASON = "Server stopped by user (Ctrl+C)."
    logger.info(SHUTDOWN_REASON)
    shutdown_event.set()

    def delayed_exit():
        time.sleep(1)
        os._exit(0)

    threading.Thread(target=delayed_exit).start()


signal.signal(signal.SIGINT, signal_handler)


@app.route("/api/events")
def events():
    """Streams server events to the client."""

    def stream():
        while not shutdown_event.is_set():
            time.sleep(0.5)
            yield ": keepalive\n\n"

        yield f"data: {json.dumps({'type': 'shutdown', 'reason': SHUTDOWN_REASON})}\n\n"

    return Response(stream_with_context(stream()), mimetype="text/event-stream")


# Configuration
project_manager = ProjectManager()


@app.route("/")
def index():
    """Renders the main page."""
    return render_template("index.html")


@app.route("/api/project/current", methods=["GET"])
def get_current_project():
    """Returns the current project path."""
    working_dir = project_manager.get_working_dir()
    return jsonify({"path": str(working_dir) if working_dir else None})


@app.route("/api/system/default-path", methods=["GET"])
def get_default_path():
    """Returns the default project path."""
    default_path = Path(user_documents_dir()) / "DeckSmith"
    try:
        default_path.mkdir(parents=True, exist_ok=True)
        return jsonify({"path": str(default_path)})
    except Exception as e:
        logger.error("Error creating default path: %s\n%s", e, traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/system/browse", methods=["POST"])
def browse_folder():
    """Opens a folder selection dialog."""
    try:
        import crossfiledialog  # pylint: disable=import-outside-toplevel

        folder_path = crossfiledialog.choose_folder(
            title="Select Project Folder",
            start_dir=str(Path.home()),
        )

        if folder_path:
            return jsonify({"path": folder_path})
        return jsonify({"path": None})
    except ImportError as e:
        logger.error("crossfiledialog import failed: %s\n%s", e, traceback.format_exc())
        return jsonify(
            {"status": "error", "message": f"Browse feature unavailable: {e}"}
        ), 501
    except Exception as e:
        logger.error("Error browsing folder: %s\n%s", e, traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/project/select", methods=["POST"])
def select_project():
    """Selects a project directory."""
    data = request.json or {}
    path_str = data.get("path")
    if not path_str:
        return jsonify({"status": "error", "message": "Path is required"}), 400

    path = Path(path_str)
    if not path.exists() or not path.is_dir():
        return jsonify({"status": "error", "message": "Directory does not exist"}), 400

    project_manager.set_working_dir(path)
    return jsonify({"status": "success", "path": str(path)})


@app.route("/api/project/close", methods=["POST"])
def close_project():
    """Closes the current project."""
    project_manager.close_project()
    return jsonify({"status": "success"})


@app.route("/api/project/create", methods=["POST"])
def create_project():
    """Creates a new project."""
    data = request.json or {}
    path_str = data.get("path")
    if not path_str:
        return jsonify({"status": "error", "message": "Path is required"}), 400

    path = Path(path_str)

    try:
        project_manager.create_project(path)
        return jsonify({"status": "success", "path": str(path)})
    except Exception as e:
        logger.error("Error creating project: %s\n%s", e, traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/load", methods=["GET"])
def load_files():
    """Loads project files."""
    data = project_manager.load_files()
    return jsonify(data)


@app.route("/api/save", methods=["POST"])
def save_files():
    """Saves project files."""
    if project_manager.get_working_dir() is None:
        return jsonify({"status": "error", "message": "No project selected"}), 400

    data = request.json
    yaml_content = data.get("yaml")
    csv_content = data.get("csv")

    try:
        project_manager.save_files(yaml_content, csv_content)
        return jsonify({"status": "success"})
    except Exception as e:
        logger.error("Error saving files: %s\n%s", e, traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/cards", methods=["GET"])
def list_cards():
    """Lists cards in the project."""
    working_dir = project_manager.get_working_dir()
    if working_dir is None:
        return jsonify([])

    csv_path = working_dir / "deck.csv"
    if not csv_path.exists():
        return jsonify([])

    try:
        csv_table = pd.read_csv(csv_path, sep=";")
        return jsonify(csv_table.to_dict(orient="records"))
    except Exception as e:
        logger.error("Error listing cards: %s\n%s", e, traceback.format_exc())
        return jsonify({"error": str(e)}), 400


@app.route("/api/preview/<int:card_index>", methods=["POST"])
def preview_card(card_index):
    """Previews a specific card."""
    working_dir = project_manager.get_working_dir()
    # Allow preview even without project, but base_path will be None

    data = request.json
    yaml_content = data.get("yaml")
    csv_content = data.get("csv")

    try:
        yaml = YAML()
        spec = yaml.load(yaml_content)
    except Exception as e:
        return jsonify({"error": f"Invalid YAML: {e}"}), 400

    try:
        csv_table = pd.read_csv(StringIO(csv_content), sep=";")
        if card_index < 0 or card_index >= len(csv_table):
            return jsonify({"error": "Index out of bounds"}), 400
        row = csv_table.iloc[card_index]
    except Exception as e:
        return jsonify({"error": f"Invalid CSV: {e}"}), 400

    try:
        row_dict = row.to_dict()
        resolved_spec = MacroResolver.resolve(spec, row_dict)

        builder = CardBuilder(resolved_spec, base_path=working_dir)
        card_image = builder.render()

        image_buffer = io.BytesIO()
        card_image.save(image_buffer, "PNG")
        image_buffer.seek(0)
        return send_file(image_buffer, mimetype="image/png")

    except Exception as e:
        logger.error("Error previewing card: %s\n%s", e, traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@app.route("/api/build", methods=["POST"])
def build_deck():
    """Builds the deck."""
    working_dir = project_manager.get_working_dir()
    if working_dir is None:
        return jsonify({"error": "No project selected"}), 400

    # Save current state first
    data = request.json
    yaml_content = data.get("yaml")
    csv_content = data.get("csv")

    try:
        project_manager.save_files(yaml_content, csv_content)

        yaml_path = working_dir / "deck.yaml"
        csv_path = working_dir / "deck.csv"
        output_path = working_dir / "output"
        output_path.mkdir(exist_ok=True)

        builder = DeckBuilder(yaml_path, csv_path)
        builder.build_deck(output_path)

        return jsonify({"status": "success", "message": f"Deck built in {output_path}"})
    except Exception as e:
        logger.error("Error building deck: %s\n%s", e, traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@app.route("/api/export", methods=["POST"])
def export_pdf():
    """Exports the deck to PDF."""
    working_dir = project_manager.get_working_dir()
    if working_dir is None:
        return jsonify({"error": "No project selected"}), 400

    data = request.json or {}

    try:
        image_folder = working_dir / "output"

        filename = data.get("filename", "deck.pdf")
        if not filename.endswith(".pdf"):
            filename += ".pdf"

        output_pdf = working_dir / filename

        if not image_folder.exists():
            return jsonify(
                {"error": "Output folder does not exist. Build deck first."}
            ), 400

        exporter = PdfExporter(
            image_folder=image_folder,
            output_path=output_pdf,
            page_size_str=data.get("page_size", "A4"),
            image_width=float(data.get("width", 63.5)),
            image_height=float(data.get("height", 88.9)),
            gap=float(data.get("gap", 0)),
            margins=(float(data.get("margin_x", 2)), float(data.get("margin_y", 2))),
        )
        exporter.export()

        return jsonify(
            {"status": "success", "message": f"PDF exported to {output_pdf}"}
        )
    except Exception as e:
        logger.error("Error exporting PDF: %s\n%s", e, traceback.format_exc())
        return jsonify({"error": str(e)}), 500


def open_browser():
    """Opens the browser."""
    webbrowser.open_new("http://127.0.0.1:5000/")


@app.route("/api/shutdown", methods=["POST"])
def shutdown():
    """Shuts down the server."""
    logger.info("Shutdown signal received. Shutting down.")
    os._exit(0)


def main():
    """Main entry point for the GUI."""
    # Open browser after a short delay to ensure server is running
    Timer(1, open_browser).start()

    serve(app, host="127.0.0.1", port=5000)


if __name__ == "__main__":
    main()
