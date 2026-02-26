"""Module: plotting shares and reconstruction."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np


def show_shares(shares: list[tuple[int, np.ndarray]], max_cols: int = 4) -> None:
    if not shares:
        raise ValueError("No shares to display.")

    total = len(shares)
    cols = min(max_cols, total)
    rows = (total + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 3 * rows))

    if rows == 1 and cols == 1:
        axes = np.array([[axes]])
    elif rows == 1:
        axes = np.array([axes])
    elif cols == 1:
        axes = np.array([[ax] for ax in axes])

    idx = 0
    for r in range(rows):
        for c in range(cols):
            ax = axes[r][c]
            if idx < total:
                x_value, share = shares[idx]
                ax.imshow(share)
                ax.set_title(f"Share x={x_value}")
            ax.axis("off")
            idx += 1
    plt.tight_layout()
    plt.show()

