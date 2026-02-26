"""Finite-field arithmetic over GF(256) used by Shamir secret sharing."""

from __future__ import annotations

import numpy as np


def _mul_byte(a: int, b: int) -> int:
    result = 0
    aa = a
    bb = b
    while bb:
        if bb & 1:
            result ^= aa
        aa <<= 1
        if aa & 0x100:
            aa ^= 0x11B
        bb >>= 1
    return result & 0xFF


def _build_mul_table() -> np.ndarray:
    table = np.zeros((256, 256), dtype=np.uint8)
    for a in range(256):
        for b in range(256):
            table[a, b] = _mul_byte(a, b)
    return table


MUL_TABLE = _build_mul_table()


def _build_inv_table() -> np.ndarray:
    inv = np.zeros(256, dtype=np.uint8)
    inv[1] = 1
    for a in range(2, 256):
        for b in range(1, 256):
            if MUL_TABLE[a, b] == 1:
                inv[a] = b
                break
    return inv


INV_TABLE = _build_inv_table()


def add(a: np.ndarray | int, b: np.ndarray | int) -> np.ndarray | int:
    return a ^ b


def mul_scalar(array: np.ndarray, scalar: int) -> np.ndarray:
    if scalar < 0 or scalar > 255:
        raise ValueError("Scalar must be in [0, 255].")
    if scalar == 0:
        return np.zeros_like(array, dtype=np.uint8)
    if scalar == 1:
        return array.astype(np.uint8, copy=True)
    return MUL_TABLE[array, scalar]


def mul_byte(a: int, b: int) -> int:
    return int(MUL_TABLE[a, b])


def div_byte(a: int, b: int) -> int:
    if b == 0:
        raise ZeroDivisionError("Division by zero in GF(256).")
    if a == 0:
        return 0
    return int(MUL_TABLE[a, INV_TABLE[b]])

