"""
This module contains the ProjectManager class for managing decksmith projects.
"""

import shutil
from pathlib import Path
from typing import Dict, Optional


class ProjectManager:
    """
    A class to manage decksmith projects.
    """

    def __init__(self):
        self.working_dir: Optional[Path] = None

    def set_working_dir(self, path: Path):
        """Sets the working directory."""
        self.working_dir = path

    def get_working_dir(self) -> Optional[Path]:
        """Returns the current working directory."""
        return self.working_dir

    def close_project(self):
        """Closes the current project."""
        self.working_dir = None

    def create_project(self, path: Path):
        """
        Creates a new project at the specified path.

        Args:
            path (Path): The path where the project directory will be created.
        """
        path.mkdir(parents=True, exist_ok=True)

        template_dir = Path(__file__).parent / "templates"

        if not (path / "deck.yaml").exists():
            shutil.copy(template_dir / "deck.yaml", path / "deck.yaml")

        if not (path / "deck.csv").exists():
            shutil.copy(template_dir / "deck.csv", path / "deck.csv")

        self.working_dir = path

    def _load_file_or_template(self, filename: str) -> str:
        """
        Helper to load a file from the working directory, or fall back to a template.

        Args:
            filename (str): The name of the file (e.g., "deck.yaml").

        Returns:
            str: The content of the file or template.
        """
        if self.working_dir is None:
            return ""

        file_path = self.working_dir / filename
        template_path = Path(__file__).parent / "templates" / filename

        if file_path.exists() and file_path.stat().st_size > 0:
            with open(file_path, "r", encoding="utf-8") as file_object:
                return file_object.read()
        elif template_path.exists():
            with open(template_path, "r", encoding="utf-8") as file_object:
                return file_object.read()
        return ""

    def load_files(self) -> Dict[str, str]:
        """
        Loads the deck.yaml and deck.csv files from the current project.

        Returns:
            Dict[str, str]: A dictionary with keys "yaml" and "csv" containing file contents.
        """
        return {
            "yaml": self._load_file_or_template("deck.yaml"),
            "csv": self._load_file_or_template("deck.csv"),
        }

    def save_files(self, yaml_content: Optional[str], csv_content: Optional[str]):
        """
        Saves the deck.yaml and deck.csv files to the current project.

        Args:
            yaml_content (Optional[str]): The content of the deck.yaml file.
            csv_content (Optional[str]): The content of the deck.csv file.

        Raises:
            ValueError: If no project is currently selected (working_dir is None).
        """
        if self.working_dir is None:
            raise ValueError("No project selected")

        if yaml_content is not None:
            with open(
                self.working_dir / "deck.yaml", "w", encoding="utf-8"
            ) as yaml_file:
                yaml_file.write(yaml_content.replace("\r\n", "\n"))

        if csv_content is not None:
            with open(self.working_dir / "deck.csv", "w", encoding="utf-8") as csv_file:
                csv_file.write(csv_content.replace("\r\n", "\n"))
