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
            path (Path): The path to create the project in.
        """
        path.mkdir(parents=True, exist_ok=True)

        # Copy templates
        # Assuming templates are in decksmith/templates relative to this file
        # But actually they are in decksmith/templates relative to the package root
        # Let's use importlib.resources or relative path from __file__
        # Since we are in decksmith/project.py, templates are in ../templates
        template_dir = Path(__file__).parent / "templates"

        if not (path / "deck.yaml").exists():
            shutil.copy(template_dir / "deck.yaml", path / "deck.yaml")

        if not (path / "deck.csv").exists():
            shutil.copy(template_dir / "deck.csv", path / "deck.csv")

        self.working_dir = path

    def load_files(self) -> Dict[str, str]:
        """
        Loads the deck.yaml and deck.csv files from the current project.
        Returns:
            Dict[str, str]: A dictionary containing the content of the files.
        """
        if self.working_dir is None:
            return {"yaml": "", "csv": ""}

        yaml_path = self.working_dir / "deck.yaml"
        csv_path = self.working_dir / "deck.csv"

        template_dir = Path(__file__).parent / "templates"
        yaml_template = template_dir / "deck.yaml"
        csv_template = template_dir / "deck.csv"

        data = {}

        # Load YAML
        if yaml_path.exists() and yaml_path.stat().st_size > 0:
            with open(yaml_path, "r", encoding="utf-8") as yaml_file:
                data["yaml"] = yaml_file.read()
        elif yaml_template.exists():
            with open(yaml_template, "r", encoding="utf-8") as yaml_template_file:
                data["yaml"] = yaml_template_file.read()
        else:
            data["yaml"] = ""

        # Load CSV
        if csv_path.exists() and csv_path.stat().st_size > 0:
            with open(csv_path, "r", encoding="utf-8") as csv_file:
                data["csv"] = csv_file.read()
        elif csv_template.exists():
            with open(csv_template, "r", encoding="utf-8") as csv_template_file:
                data["csv"] = csv_template_file.read()
        else:
            data["csv"] = ""

        return data

    def save_files(self, yaml_content: Optional[str], csv_content: Optional[str]):
        """
        Saves the deck.yaml and deck.csv files to the current project.
        Args:
            yaml_content (Optional[str]): The content of the deck.yaml file.
            csv_content (Optional[str]): The content of the deck.csv file.
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
