"""Crypto GUI mixin: encryption and decryption tabs."""

from __future__ import annotations

from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .decryption_module import reconstruct_image
from .encryption_module import generate_shares, validate_parameters
from .image_io import load_rgb_image, load_share, save_rgb_image, save_shares
from .visualization_module import show_shares


class GuiCryptoMixin:
    def _build_encrypt_tab(self) -> None:
        body = ttk.Frame(self.encrypt_tab, style="App.TFrame")
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=0)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        controls = ttk.LabelFrame(body, text="Parametri i akcije", style="Section.TLabelframe", padding=12)
        controls.grid(row=0, column=0, sticky="nsw", padx=(0, 12))

        ttk.Button(controls, text="Ucitaj sliku", style="Accent.TButton", command=self._encrypt_load_image).grid(
            row=0, column=0, padx=4, pady=4, sticky="w"
        )
        self.encrypt_image_var = self._string_var("Nije ucitana slika.")
        ttk.Label(
            controls,
            textvariable=self.encrypt_image_var,
            style="Path.TLabel",
            wraplength=310,
            justify="left",
        ).grid(
            row=1, column=0, padx=4, pady=(2, 10), sticky="w"
        )

        ttk.Label(controls, text="n (broj senki):").grid(row=2, column=0, padx=4, pady=(2, 2), sticky="w")
        self.encrypt_n_entry = ttk.Entry(controls, width=10)
        self.encrypt_n_entry.insert(0, "5")
        self.encrypt_n_entry.grid(row=3, column=0, padx=4, pady=(0, 8), sticky="w")

        ttk.Label(controls, text="k (prag):").grid(row=4, column=0, padx=4, pady=(2, 2), sticky="w")
        self.encrypt_k_entry = ttk.Entry(controls, width=10)
        self.encrypt_k_entry.insert(0, "3")
        self.encrypt_k_entry.grid(row=5, column=0, padx=4, pady=(0, 8), sticky="w")

        ttk.Label(controls, text="seed (opciono):").grid(row=6, column=0, padx=4, pady=(2, 2), sticky="w")
        self.encrypt_seed_entry = ttk.Entry(controls, width=12)
        self.encrypt_seed_entry.grid(row=7, column=0, padx=4, pady=(0, 12), sticky="w")

        ttk.Button(
            controls,
            text="Generisi i sacuvaj senke",
            style="Accent.TButton",
            command=self._encrypt_generate_shares,
        ).grid(row=8, column=0, padx=4, pady=4, sticky="w")
        ttk.Button(
            controls,
            text="Prikazi trenutno generisane senke",
            style="Ghost.TButton",
            command=self._encrypt_preview_shares,
        ).grid(row=9, column=0, padx=4, pady=4, sticky="w")

        preview_box = ttk.LabelFrame(body, text="Originalna slika", style="Section.TLabelframe", padding=10)
        preview_box.grid(row=0, column=1, sticky="nsew")
        preview_box.columnconfigure(0, weight=1)
        preview_box.rowconfigure(0, weight=1)

        self.encrypt_preview_label = ttk.Label(preview_box, text="Nema ucitane slike.", style="Image.TLabel")
        self.encrypt_preview_label.grid(row=0, column=0, sticky="nsew")

    def _build_decrypt_tab(self) -> None:
        body = ttk.Frame(self.decrypt_tab, style="App.TFrame")
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=0)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        controls = ttk.LabelFrame(body, text="Akcije", style="Section.TLabelframe", padding=12)
        controls.grid(row=0, column=0, sticky="nsw", padx=(0, 12))

        ttk.Button(
            controls,
            text="Ucitaj senke (>1)",
            style="Accent.TButton",
            command=self._decrypt_select_shares,
        ).grid(row=0, column=0, padx=4, pady=4, sticky="w")
        self.decrypt_count_var = self._string_var("Izabrano senki: 0")
        ttk.Label(controls, textvariable=self.decrypt_count_var, style="Path.TLabel").grid(
            row=1, column=0, padx=4, pady=(2, 10), sticky="w"
        )

        ttk.Button(
            controls,
            text="Sacuvaj rekonstruisanu sliku",
            style="Ghost.TButton",
            command=self._decrypt_save_reconstructed,
        ).grid(row=2, column=0, padx=4, pady=4, sticky="w")

        preview_box = ttk.LabelFrame(body, text="Rekonstruisana slika", style="Section.TLabelframe", padding=10)
        preview_box.grid(row=0, column=1, sticky="nsew")
        preview_box.columnconfigure(0, weight=1)
        preview_box.rowconfigure(0, weight=1)

        self.decrypt_preview_label = ttk.Label(preview_box, text="Nema rekonstrukcije.", style="Image.TLabel")
        self.decrypt_preview_label.grid(row=0, column=0, sticky="nsew")

    def _encrypt_load_image(self) -> None:
        path = self._load_image_dialog("Izaberi sliku za enkripciju")
        if not path:
            return
        try:
            self.encrypt_image_path = Path(path)
            self.encrypt_image = load_rgb_image(path)
            self.encrypt_image_var.set(str(self.encrypt_image_path))
            self._render_preview(self.encrypt_preview_label, self.encrypt_image, "encrypt_original")
            self._log(f"Enkripcija: ucitana slika {self.encrypt_image_path.name}")
        except Exception as exc:  # pragma: no cover
            messagebox.showerror("Greska", str(exc))

    def _encrypt_get_parameters(self) -> tuple[int, int, int | None]:
        try:
            n_value = int(self.encrypt_n_entry.get().strip())
            k_value = int(self.encrypt_k_entry.get().strip())
            seed_raw = self.encrypt_seed_entry.get().strip()
            seed_value = int(seed_raw) if seed_raw else None
            validate_parameters(n_value, k_value)
        except ValueError as exc:
            raise ValueError(f"Neispravni parametri: {exc}") from exc
        return n_value, k_value, seed_value

    def _encrypt_generate_shares(self) -> None:
        if self.encrypt_image is None:
            messagebox.showwarning("Upozorenje", "Prvo ucitaj sliku na tabu Enkripcija.")
            return
        try:
            n_value, k_value, seed_value = self._encrypt_get_parameters()
            self.generated_shares = generate_shares(self.encrypt_image, n_value, k_value, seed_value)

            output_dir = filedialog.askdirectory(title="Izaberi folder za cuvanje senki")
            if not output_dir:
                self._log("Enkripcija: cuvanje senki otkazano.")
                return

            saved_paths = save_shares(self.generated_shares, output_dir, prefix="share")
            self._log(
                f"Enkripcija: sacuvano {len(saved_paths)} senki u '{output_dir}' (k={k_value}, n={n_value})."
            )
        except Exception as exc:  # pragma: no cover
            messagebox.showerror("Greska", str(exc))

    def _encrypt_preview_shares(self) -> None:
        if not self.generated_shares:
            messagebox.showinfo("Informacija", "Nema generisanih senki za prikaz.")
            return
        show_shares(self.generated_shares)

    def _decrypt_select_shares(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Izaberi senke za dekripciju",
            filetypes=[("PNG files", "*.png")],
        )
        if not paths:
            return
        if len(paths) == 1:
            self.decrypt_share_paths = []
            self.decrypt_count_var.set("Izabrano senki: 1")
            messagebox.showerror("Greska", "Za dekripciju moras izabrati najmanje 2 senke.")
            self._log("Dekripcija: greska - izabrana je samo 1 senka.")
            return
        self.decrypt_share_paths = list(paths)
        self.decrypt_count_var.set(f"Izabrano senki: {len(self.decrypt_share_paths)}")
        self._log(f"Dekripcija: izabrano {len(self.decrypt_share_paths)} senki.")
        self._decrypt_reconstruct()

    def _decrypt_reconstruct(self) -> None:
        if len(self.decrypt_share_paths) < 2:
            return
        try:
            loaded_shares = [load_share(path) for path in self.decrypt_share_paths]
            self.reconstructed_image = reconstruct_image(loaded_shares, len(loaded_shares))
            self._render_preview(self.decrypt_preview_label, self.reconstructed_image, "decrypt_reconstructed")
            self._log(f"Dekripcija: rekonstrukcija uspesna sa {len(loaded_shares)} senki.")
        except Exception as exc:  # pragma: no cover
            messagebox.showerror("Greska", str(exc))

    def _decrypt_save_reconstructed(self) -> None:
        if self.reconstructed_image is None:
            messagebox.showinfo("Informacija", "Nema rekonstruisane slike za cuvanje.")
            return

        save_path = filedialog.asksaveasfilename(
            title="Sacuvaj rekonstruisanu sliku",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")],
            initialfile="reconstructed.png",
        )
        if not save_path:
            return
        try:
            save_rgb_image(self.reconstructed_image, save_path)
            self._log(f"Dekripcija: rekonstruisana slika sacuvana na {save_path}.")
        except Exception as exc:  # pragma: no cover
            messagebox.showerror("Greska", str(exc))

