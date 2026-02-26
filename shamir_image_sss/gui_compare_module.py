"""Compare GUI mixin: image A/B loading and metrics."""

from __future__ import annotations

from pathlib import Path
from tkinter import messagebox, ttk

import numpy as np

from .evaluation_module import mse, psnr
from .image_io import load_rgb_image


class GuiCompareMixin:
    def _build_compare_tab(self) -> None:
        body = ttk.Frame(self.compare_tab, style="App.TFrame")
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=1)
        body.rowconfigure(1, weight=1)

        controls = ttk.LabelFrame(body, text="Poredjenje slika", style="Section.TLabelframe", padding=12)
        controls.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        controls.columnconfigure(1, weight=1)

        ttk.Button(controls, text="Ucitaj sliku A", style="Accent.TButton", command=self._compare_load_a).grid(
            row=0, column=0, padx=4, pady=4, sticky="w"
        )
        self.compare_path_a_var = self._string_var("Slika A nije ucitana.")
        ttk.Label(
            controls,
            textvariable=self.compare_path_a_var,
            style="Path.TLabel",
            wraplength=720,
            justify="left",
        ).grid(
            row=0, column=1, padx=4, pady=4, sticky="w"
        )

        ttk.Button(controls, text="Ucitaj sliku B", style="Accent.TButton", command=self._compare_load_b).grid(
            row=1, column=0, padx=4, pady=4, sticky="w"
        )
        self.compare_path_b_var = self._string_var("Slika B nije ucitana.")
        ttk.Label(
            controls,
            textvariable=self.compare_path_b_var,
            style="Path.TLabel",
            wraplength=720,
            justify="left",
        ).grid(
            row=1, column=1, padx=4, pady=4, sticky="w"
        )

        ttk.Button(
            controls,
            text="Izracunaj MSE / PSNR",
            style="Ghost.TButton",
            command=self._compare_compute,
        ).grid(
            row=2, column=0, padx=4, pady=4, sticky="w"
        )
        self.compare_metrics_var = self._string_var("MSE: -, PSNR: -")
        ttk.Label(
            controls,
            textvariable=self.compare_metrics_var,
            style="Path.TLabel",
            font=("Segoe UI Semibold", 10),
        ).grid(
            row=2, column=1, padx=4, pady=4, sticky="w"
        )

        previews = ttk.Frame(body, style="App.TFrame")
        previews.grid(row=1, column=0, sticky="nsew")
        previews.columnconfigure(0, weight=1)
        previews.columnconfigure(1, weight=1)
        previews.rowconfigure(0, weight=1)

        left_box = ttk.LabelFrame(previews, text="Slika A", style="Section.TLabelframe", padding=10)
        left_box.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        left_box.columnconfigure(0, weight=1)
        left_box.rowconfigure(0, weight=1)
        self.compare_preview_a = ttk.Label(left_box, text="Nema slike A.", style="Image.TLabel")
        self.compare_preview_a.grid(row=0, column=0, sticky="nsew")

        right_box = ttk.LabelFrame(previews, text="Slika B", style="Section.TLabelframe", padding=10)
        right_box.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        right_box.columnconfigure(0, weight=1)
        right_box.rowconfigure(0, weight=1)
        self.compare_preview_b = ttk.Label(right_box, text="Nema slike B.", style="Image.TLabel")
        self.compare_preview_b.grid(row=0, column=0, sticky="nsew")

    def _compare_load_a(self) -> None:
        path = self._load_image_dialog("Izaberi sliku A")
        if not path:
            return
        try:
            self.compare_path_a = Path(path)
            self.compare_image_a = load_rgb_image(path)
            self.compare_path_a_var.set(str(self.compare_path_a))
            self._render_preview(self.compare_preview_a, self.compare_image_a, "compare_a")
            self._log(f"Poredjenje: ucitana slika A ({self.compare_path_a.name}).")
        except Exception as exc:  # pragma: no cover
            messagebox.showerror("Greska", str(exc))

    def _compare_load_b(self) -> None:
        path = self._load_image_dialog("Izaberi sliku B")
        if not path:
            return
        try:
            self.compare_path_b = Path(path)
            self.compare_image_b = load_rgb_image(path)
            self.compare_path_b_var.set(str(self.compare_path_b))
            self._render_preview(self.compare_preview_b, self.compare_image_b, "compare_b")
            self._log(f"Poredjenje: ucitana slika B ({self.compare_path_b.name}).")
        except Exception as exc:  # pragma: no cover
            messagebox.showerror("Greska", str(exc))

    def _compare_compute(self) -> None:
        if self.compare_image_a is None or self.compare_image_b is None:
            messagebox.showwarning("Upozorenje", "Ucitaj obe slike (A i B).")
            return
        try:
            mse_value = mse(self.compare_image_a, self.compare_image_b)
            psnr_value = psnr(self.compare_image_a, self.compare_image_b)
            psnr_text = "inf" if np.isinf(psnr_value) else f"{psnr_value:.6f}"
            self.compare_metrics_var.set(f"MSE: {mse_value:.8f}, PSNR: {psnr_text} dB")
            self._log(f"Poredjenje: MSE={mse_value:.8f}, PSNR={psnr_text} dB.")
        except Exception as exc:  # pragma: no cover
            messagebox.showerror("Greska", str(exc))

