from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

import numpy as np
from PIL import Image, ImageTk

from .gui_compare_module import GuiCompareMixin
from .gui_crypto_module import GuiCryptoMixin


class ShamirGUI(GuiCryptoMixin, GuiCompareMixin, tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Shamir Secret Sharing - Full")
        self.geometry("1050x740")
        self.minsize(940, 650)

        self._bg = "#EAF0F5"
        self._card = "#FFFFFF"
        self._text_main = "#1B344A"
        self._text_soft = "#577086"
        self._accent = "#0F766E"
        self._accent_hover = "#0D675F"
        self._ghost = "#D8E7F2"

        self.encrypt_image_path: Path | None = None
        self.encrypt_image: np.ndarray | None = None
        self.generated_shares: list[tuple[int, np.ndarray]] = []

        self.decrypt_share_paths: list[str] = []
        self.reconstructed_image: np.ndarray | None = None

        self.compare_image_a: np.ndarray | None = None
        self.compare_image_b: np.ndarray | None = None
        self.compare_path_a: Path | None = None
        self.compare_path_b: Path | None = None

        self._photo_refs: dict[str, ImageTk.PhotoImage] = {}

        self._configure_style()
        self._build_layout()

    def _string_var(self, value: str) -> tk.StringVar:
        return tk.StringVar(value=value)

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        self.configure(bg=self._bg)

        style.configure(".", font=("Segoe UI", 10))
        style.configure("App.TFrame", background=self._bg)
        style.configure("Card.TFrame", background=self._card)

        style.configure(
            "Header.TLabel",
            background=self._card,
            foreground=self._text_main,
            font=("Segoe UI Semibold", 17),
        )
        style.configure(
            "Subheader.TLabel",
            background=self._card,
            foreground=self._text_soft,
            font=("Segoe UI", 10),
        )
        style.configure("Path.TLabel", background=self._bg, foreground=self._text_soft)

        style.configure(
            "Section.TLabelframe",
            background=self._bg,
            borderwidth=0,
            relief="flat",
        )
        style.configure(
            "Section.TLabelframe.Label",
            background=self._bg,
            foreground=self._text_main,
            font=("Segoe UI Semibold", 11),
        )

        style.configure(
            "Accent.TButton",
            background=self._accent,
            foreground="#FFFFFF",
            borderwidth=0,
            focusthickness=0,
            padding=(12, 8),
            font=("Segoe UI Semibold", 10),
        )
        style.map(
            "Accent.TButton",
            background=[("pressed", self._accent_hover), ("active", self._accent_hover)],
            foreground=[("disabled", "#D0D7DE")],
        )

        style.configure(
            "Ghost.TButton",
            background=self._ghost,
            foreground="#18445D",
            borderwidth=0,
            focusthickness=0,
            padding=(12, 8),
            font=("Segoe UI", 10),
        )
        style.map(
            "Ghost.TButton",
            background=[("pressed", "#C9DCEB"), ("active", "#CFE1EE")],
        )

        style.configure(
            "TNotebook",
            background=self._bg,
            borderwidth=0,
            tabmargins=(0, 6, 0, 0),
        )
        style.configure(
            "TNotebook.Tab",
            background="#D6E1EA",
            foreground="#2B4C65",
            padding=(14, 8),
            font=("Segoe UI Semibold", 10),
            borderwidth=0,
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", self._card), ("active", "#E2EAF1")],
            foreground=[("selected", "#17354E")],
        )

        style.configure("Image.TLabel", background=self._card, foreground=self._text_soft, anchor="center")
        style.configure("TEntry", fieldbackground="#FFFFFF")

    def _build_layout(self) -> None:
        root = ttk.Frame(self, style="App.TFrame", padding=(14, 14, 14, 10))
        root.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(root, style="Card.TFrame", padding=(16, 12))
        header.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(header, text="Shamir Secret Sharing - Full GUI", style="Header.TLabel").pack(anchor=tk.W)
        ttk.Label(
            header,
            text="Enkripcija, dekripcija i poredjenje u jednom prozoru.",
            style="Subheader.TLabel",
        ).pack(anchor=tk.W, pady=(4, 0))

        notebook = ttk.Notebook(root)
        notebook.pack(fill=tk.BOTH, expand=True)

        self.encrypt_tab = ttk.Frame(notebook, padding=12)
        self.decrypt_tab = ttk.Frame(notebook, padding=12)
        self.compare_tab = ttk.Frame(notebook, padding=12)

        notebook.add(self.encrypt_tab, text="1) Enkripcija")
        notebook.add(self.decrypt_tab, text="2) Dekripcija")
        notebook.add(self.compare_tab, text="3) Compare")

        self._build_encrypt_tab()
        self._build_decrypt_tab()
        self._build_compare_tab()

        log_frame = ttk.LabelFrame(root, text="Status", padding=8, style="Section.TLabelframe")
        log_frame.pack(fill=tk.BOTH, pady=(10, 0))
        self.log_text = tk.Text(log_frame, height=8, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.configure(
            state=tk.DISABLED,
            bg="#F9FCFF",
            fg=self._text_main,
            relief=tk.FLAT,
            padx=10,
            pady=8,
            insertbackground=self._text_main,
        )

    def _log(self, message: str) -> None:
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _render_preview(self, target: ttk.Label, image_array: np.ndarray, key: str) -> None:
        image = Image.fromarray(image_array.astype(np.uint8), mode="RGB")
        image.thumbnail((480, 420))
        photo = ImageTk.PhotoImage(image)
        self._photo_refs[key] = photo
        target.configure(image=photo, text="")

    def _load_image_dialog(self, title: str) -> str:
        return filedialog.askopenfilename(
            title=title,
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")],
        )


ShamirCompareGUI = ShamirGUI


def run_gui() -> None:
    app = ShamirGUI()
    app.mainloop()


def run_compare_gui() -> None:
    run_gui()
