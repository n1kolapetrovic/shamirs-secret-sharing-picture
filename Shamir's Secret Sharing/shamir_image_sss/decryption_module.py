"""Module: image reconstruction (decryption side)."""

from __future__ import annotations

import numpy as np

from .gf256 import add, div_byte, mul_byte, mul_scalar


def _lagrange_basis_at_zero(x_values: list[int]) -> list[int]:
    lambdas: list[int] = []
    for i, x_i in enumerate(x_values):
        numerator = 1
        denominator = 1
        for j, x_j in enumerate(x_values):
            if i == j:
                continue
            numerator = mul_byte(numerator, x_j)
            denominator = mul_byte(denominator, x_j ^ x_i)
        lambdas.append(div_byte(numerator, denominator))
    return lambdas


def reconstruct_image(shares: list[tuple[int, np.ndarray]], k: int) -> np.ndarray:
    if len(shares) < k:
        raise ValueError("Not enough shares for reconstruction.")

    selected = shares[:k]
    x_values = [x for x, _ in selected]

    if len(set(x_values)) != len(x_values):
        raise ValueError("Shares must have distinct x values.")
    if any(not (1 <= x <= 255) for x in x_values):
        raise ValueError("x values must be in range [1, 255].")

    base_shape = selected[0][1].shape
    for _, share_image in selected:
        if share_image.shape != base_shape:
            raise ValueError("All shares must have the same dimensions.")

    lambdas = _lagrange_basis_at_zero(x_values)
    reconstructed = np.zeros(base_shape, dtype=np.uint8)

    for (x_value, share_image), lambda_i in zip(selected, lambdas):
        _ = x_value
        reconstructed = add(reconstructed, mul_scalar(share_image.astype(np.uint8), lambda_i))

    return reconstructed
