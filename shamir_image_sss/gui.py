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
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        start_w = min(1050, max(760, screen_w - 80))
        start_h = min(740, max(520, screen_h - 120))
        self.geometry(f"{start_w}x{start_h}")
        self.minsize(640, 420)

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
        root.columnconfigure(0, weight=1)
        root.rowconfigure(1, weight=1)
        root.rowconfigure(2, weight=0, minsize=120)

        header = ttk.Frame(root, style="Card.TFrame", padding=(16, 12))
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(header, text="Shamir Secret Sharing", style="Header.TLabel").pack(anchor=tk.W)

        notebook = ttk.Notebook(root)
        notebook.grid(row=1, column=0, sticky="nsew")

        self.encrypt_tab = self._create_scrollable_tab(notebook, "1) Enkripcija")
        self.decrypt_tab = self._create_scrollable_tab(notebook, "2) Dekripcija")
        self.compare_tab = self._create_scrollable_tab(notebook, "3) Compare")

        self._build_encrypt_tab()
        self._build_decrypt_tab()
        self._build_compare_tab()

        log_frame = ttk.LabelFrame(root, text="Status", padding=8, style="Section.TLabelframe")
        log_frame.grid(row=2, column=0, sticky="nsew", pady=(10, 0))
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

    def _create_scrollable_tab(self, notebook: ttk.Notebook, title: str) -> ttk.Frame:
        tab_outer = ttk.Frame(notebook, style="App.TFrame")
        notebook.add(tab_outer, text=title)

        canvas = tk.Canvas(
            tab_outer,
            bg=self._bg,
            highlightthickness=0,
            borderwidth=0,
        )
        scrollbar = ttk.Scrollbar(tab_outer, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        content = ttk.Frame(canvas, style="App.TFrame", padding=12)
        window_id = canvas.create_window((0, 0), window=content, anchor="nw")

        def on_content_configure(_event: tk.Event) -> None:
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event: tk.Event) -> None:
            canvas.itemconfigure(window_id, width=event.width)

        def on_mousewheel(event: tk.Event) -> None:
            delta = int(-1 * (event.delta / 120))
            if delta != 0:
                canvas.yview_scroll(delta, "units")

        def bind_mousewheel(_event: tk.Event) -> None:
            canvas.bind_all("<MouseWheel>", on_mousewheel)

        def unbind_mousewheel(_event: tk.Event) -> None:
            canvas.unbind_all("<MouseWheel>")

        content.bind("<Configure>", on_content_configure)
        canvas.bind("<Configure>", on_canvas_configure)
        canvas.bind("<Enter>", bind_mousewheel)
        canvas.bind("<Leave>", unbind_mousewheel)

        return content

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
