"""Image and share I/O helpers."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

import numpy as np
from PIL import Image


SHARE_NAME_PATTERN = re.compile(r".*_x(?P<x>\d+)\.png$", re.IGNORECASE)


def load_rgb_image(path: str | Path) -> np.ndarray:
    image = Image.open(path).convert("RGB")
    return np.array(image, dtype=np.uint8)


def save_rgb_image(image_array: np.ndarray, path: str | Path) -> None:
    image = Image.fromarray(image_array.astype(np.uint8), mode="RGB")
    image.save(path)


def save_shares(
    shares: Iterable[tuple[int, np.ndarray]],
    output_dir: str | Path,
    prefix: str = "share",
) -> list[Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    saved_paths: list[Path] = []
    for x_value, share_image in shares:
        share_file = output_path / f"{prefix}_x{x_value:03d}.png"
        save_rgb_image(share_image, share_file)
        saved_paths.append(share_file)
    return saved_paths


def parse_x_from_share_filename(path: str | Path) -> int:
    match = SHARE_NAME_PATTERN.match(Path(path).name)
    if not match:
        raise ValueError(
            f"Filename '{Path(path).name}' does not match expected format '*_xNNN.png'."
        )
    x_value = int(match.group("x"))
    if not 1 <= x_value <= 255:
        raise ValueError("x value in filename must be in range [1, 255].")
    return x_value


def load_share(path: str | Path) -> tuple[int, np.ndarray]:
    x_value = parse_x_from_share_filename(path)
    share_image = load_rgb_image(path)
    return x_value, share_image
