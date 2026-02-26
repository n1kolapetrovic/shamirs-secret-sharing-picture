"""Module: image share generation (encryption side)."""

from __future__ import annotations

from typing import Optional

import numpy as np

from .gf256 import add, mul_scalar


def validate_parameters(n: int, k: int) -> None:
    if not (2 <= k <= n <= 255):
        raise ValueError("Parameters must satisfy 2 <= k <= n <= 255.")


def generate_shares(
    image_array: np.ndarray,
    n: int,
    k: int,
    seed: Optional[int] = None,
) -> list[tuple[int, np.ndarray]]:
    validate_parameters(n, k)
    if image_array.dtype != np.uint8:
        image_array = image_array.astype(np.uint8)
    if image_array.ndim != 3 or image_array.shape[2] != 3:
        raise ValueError("Input image must be an RGB array of shape (H, W, 3).")

    rng = np.random.default_rng(seed)
    h, w, c = image_array.shape
    random_coeffs = rng.integers(0, 256, size=(k - 1, h, w, c), dtype=np.uint8)
    shares: list[tuple[int, np.ndarray]] = []

    for x_value in range(1, n + 1):
        y = random_coeffs[-1].copy()
        for idx in range(k - 3, -1, -1):
            y = add(mul_scalar(y, x_value), random_coeffs[idx])
        y = add(mul_scalar(y, x_value), image_array)
        shares.append((x_value, y.astype(np.uint8)))
    return shares

