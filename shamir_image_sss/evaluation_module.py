"""Module: reconstruction quality metrics (MSE / PSNR)."""

from __future__ import annotations

import numpy as np


def mse(original: np.ndarray, reconstructed: np.ndarray) -> float:
    if original.shape != reconstructed.shape:
        raise ValueError("Original and reconstructed images must have identical shapes.")
    diff = original.astype(np.float64) - reconstructed.astype(np.float64)
    return float(np.mean(diff ** 2))


def psnr(original: np.ndarray, reconstructed: np.ndarray, max_pixel: float = 255.0) -> float:
    error = mse(original, reconstructed)
    if error == 0.0:
        return float("inf")
    return float(10.0 * np.log10((max_pixel ** 2) / error))

