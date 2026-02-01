"""
This module provides the functionality to export images from a folder to a PDF file.
"""

from pathlib import Path
from typing import List, Tuple

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from decksmith.logger import logger


class PdfExporter:
    """
    A class to export images from a folder to a PDF file.
    """

    def __init__(
        self,
        image_folder: Path,
        output_path: Path,
        page_size_str: str = "A4",
        image_width: float = 63,
        image_height: float = 88,
        gap: float = 0,
        margins: Tuple[float, float] = (2, 2),
    ):
        self.image_folder = image_folder
        self.image_paths = self._get_image_paths()
        self.output_path = output_path
        self.page_size = self._get_page_size(page_size_str)
        self.image_width = image_width * mm
        self.image_height = image_height * mm
        self.gap = gap * mm
        self.margins = (margins[0] * mm, margins[1] * mm)
        self.pdf = canvas.Canvas(str(self.output_path), pagesize=self.page_size)

    def _get_image_paths(self) -> List[Path]:
        """
        Scans the image folder and returns a list of image paths.

        Returns:
            List[str]: A sorted list of image paths.
        """
        image_extensions = {".png", ".jpg", ".jpeg", ".webp"}
        return sorted(
            [
                image_path
                for image_path in self.image_folder.iterdir()
                if image_path.suffix.lower() in image_extensions
            ]
        )

    def _get_page_size(self, page_size_str: str) -> Tuple[float, float]:
        """
        Returns the page size from a string.

        Args:
            page_size_str (str): The string representing the page size.

        Returns:
            Tuple[float, float]: The page size in points.
        """
        if page_size_str.lower() == "a4":
            return A4
        # Add other page sizes here if needed
        return A4

    def _calculate_layout(self, page_width: float, page_height: float):
        """
        Calculates the optimal layout for the images on the page.

        Args:
            page_width (float): The width of the page.
            page_height (float): The height of the page.

        Returns:
            Tuple[int, int, bool]: The number of columns, rows, and if the layout is rotated.
        """
        best_fit = 0
        best_layout = (0, 0, False)

        for rotated in [False, True]:
            image_width, image_height = (
                (self.image_width, self.image_height)
                if not rotated
                else (self.image_height, self.image_width)
            )

            cols = int(
                (page_width - 2 * self.margins[0] + self.gap) / (image_width + self.gap)
            )
            rows = int(
                (page_height - 2 * self.margins[1] + self.gap)
                / (image_height + self.gap)
            )

            if cols * rows > best_fit:
                best_fit = cols * rows
                best_layout = (cols, rows, rotated)

        return best_layout

    def export(self):
        """
        Exports the images to a PDF file.
        """
        try:
            page_width, page_height = self.page_size
            cols, rows, rotated = self._calculate_layout(page_width, page_height)

            if cols == 0 or rows == 0:
                raise ValueError("The images are too large to fit on the page.")

            image_width, image_height = (
                (self.image_width, self.image_height)
                if not rotated
                else (self.image_height, self.image_width)
            )

            total_width = cols * image_width + (cols - 1) * self.gap
            total_height = rows * image_height + (rows - 1) * self.gap
            start_horizontal = (page_width - total_width) / 2
            start_vertical = (page_height - total_height) / 2

            images_on_page = 0
            for image_path in self.image_paths:
                if images_on_page > 0 and images_on_page % (cols * rows) == 0:
                    self.pdf.showPage()
                    images_on_page = 0

                row = images_on_page // cols
                col = images_on_page % cols

                position_horizontal = start_horizontal + col * (image_width + self.gap)
                position_vertical = start_vertical + row * (image_height + self.gap)

                if not rotated:
                    self.pdf.drawImage(
                        str(image_path),
                        position_horizontal,
                        position_vertical,
                        width=image_width,
                        height=image_height,
                        preserveAspectRatio=True,
                    )
                else:
                    self.pdf.saveState()
                    center_horizontal = position_horizontal + image_width / 2
                    center_vertical = position_vertical + image_height / 2
                    self.pdf.translate(center_horizontal, center_vertical)
                    self.pdf.rotate(90)
                    self.pdf.drawImage(
                        str(image_path),
                        -image_height / 2,
                        -image_width / 2,
                        width=image_height,
                        height=image_width,
                        preserveAspectRatio=True,
                    )
                    self.pdf.restoreState()
                images_on_page += 1

            self.pdf.save()
            logger.info("Successfully exported PDF to %s", self.output_path)
        except Exception as e:
            logger.error("An error occurred during PDF export: %s", e)
            raise
