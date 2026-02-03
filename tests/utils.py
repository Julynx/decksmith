from pathlib import Path
from typing import Tuple

import numpy as np
from PIL import Image


def compare_images(img1_path: Path, img2_path: Path) -> Tuple[float, float, float]:
    """
    Compares two images and returns difference metrics.

    Args:
        img1_path (Path): Path to the first image.
        img2_path (Path): Path to the second image.

    Returns:
        Tuple[float, float, float]: A tuple containing:
            - max_diff (float): Maximum pixel difference (0-255).
            - avg_diff (float): Average pixel difference.
            - percent_diff (float): Percentage of pixels that are different.

    Raises:
        ValueError: If images have different sizes or cannot be opened.
    """
    try:
        img1 = Image.open(img1_path).convert("RGBA")
        img2 = Image.open(img2_path).convert("RGBA")
    except Exception as e:
        raise ValueError(f"Error opening images: {e}")

    if img1.size != img2.size:
        raise ValueError(f"Images have different sizes: {img1.size} vs {img2.size}")

    arr1 = np.array(img1)
    arr2 = np.array(img2)

    diff = np.abs(arr1.astype(int) - arr2.astype(int))
    max_diff = np.max(diff)
    avg_diff = np.mean(diff)

    # Count pixels that are different (any channel difference > 0)
    diff_pixels = np.sum(np.any(diff > 0, axis=2))
    total_pixels = img1.size[0] * img1.size[1]
    percent_diff = (diff_pixels / total_pixels) * 100

    return max_diff, avg_diff, percent_diff
