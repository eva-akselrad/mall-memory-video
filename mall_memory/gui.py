from __future__ import annotations

import os
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from mall_memory import __version__
from mall_memory.demo_music import bundled_demo_path, generate_mp3
from mall_memory.effects import PRESETS
from mall_memory.images import discover_images
from mall_memory.render import build_video

PHASE_LABELS = {
    "loading": "Loading photos…",
    "slides": "Building slides…",
    "audio": "Mixing music…",
    "encoding": "Encoding video…",
    "done": "Done!",
}


class MallMemoryApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"Mall Memory Video · v{__version__}")
        self.minsize(560, 520)
        self.geometry("640x580")
        self.configure(bg="#14161c")

        self._images_dir = tk.StringVar()
        self._music_path = tk.StringVar()
        self._output_path = tk.StringVar(value=str(Path("output") / "mall-memory.mp4"))
        self._style = tk.StringVar(value="proper-people")
        self._sort = tk.StringVar(value="name")
        self._use_custom_timing = tk.BooleanVar(value=False)
        self._seconds = tk.DoubleVar(value=PRESETS["proper-people"].seconds_per_image)
        self._crossfade = tk.DoubleVar(value=PRESETS["proper-people"].crossfade_seconds)
        self._status = tk.StringVar(value="Pick your mall photos and a music track.")
        self._photo_count = tk.StringVar(value="")
        self._busy = False

        self._build_styles()
        self._build_layout()
        self._style.trace_add("write", self._on_style_change)

    def _build_styles(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        bg = "#14161c"
        panel = "#1c1f28"
        fg = "#e8e6e3"
        muted = "#9aa3b2"
        accent = "#6ec8c9"

        style.configure(".", background=bg, foreground=fg, fieldbackground=panel)
        style.configure("TFrame", background=bg)
        style.configure("Card.TFrame", background=panel)
        style.configure("TLabel", background=bg, foreground=fg)
        style.configure("Card.TLabel", background=panel, foreground=fg)
        style.configure("Muted.TLabel", background=bg, foreground=muted, font=("Segoe UI", 9))
        style.configure("Title.TLabel", background=bg, foreground=fg, font=("Segoe UI", 16, "bold"))
        style.configure("TButton", padding=(10, 6))
        style.configure("Accent.TButton", foreground="#0d1117")
        style.map("Accent.TButton", background=[("active", "#8ed9da"), ("!disabled", accent)])
        style.configure("TEntry", fieldbackground="#252a35", foreground=fg)
        style.configure("TCombobox", fieldbackground="#252a35", foreground=fg)
        style.configure("Horizontal.TProgressbar", troughcolor=panel, background=accent)

    def _build_layout(self) -> None:
        outer = ttk.Frame(self, padding=20)
        outer.pack(fill=tk.BOTH, expand=True)

        ttk.Label(outer, text="Mall Memory Video", style="Title.TLabel").pack(anchor=tk.W)
        ttk.Label(
            outer,
            text="Slow cinematic slideshow with music — documentary mall vibes.",
            style="Muted.TLabel",
        ).pack(anchor=tk.W, pady=(4, 16))

        card = ttk.Frame(outer, style="Card.TFrame", padding=16)
        card.pack(fill=tk.BOTH, expand=True)

        self._row_path(card, "Photos folder", self._images_dir, self._pick_images, 0)
        ttk.Label(card, textvariable=self._photo_count, style="Muted.TLabel").grid(
            row=1, column=1, sticky=tk.W, pady=(0, 8)
        )
        self._row_path(card, "Music track", self._music_path, self._pick_music, 2)
        music_actions = ttk.Frame(card, style="Card.TFrame")
        music_actions.grid(row=3, column=1, columnspan=2, sticky=tk.W, pady=(0, 8))
        ttk.Button(music_actions, text="Use demo music", command=self._use_demo_music).pack(
            side=tk.LEFT, padx=(0, 8)
        )
        ttk.Button(music_actions, text="Generate demo track", command=self._generate_demo_music).pack(
            side=tk.LEFT
        )
        self._row_path(card, "Save video as", self._output_path, self._pick_output, 4)

        opts = ttk.Frame(card, style="Card.TFrame")
        opts.grid(row=6, column=0, columnspan=3, sticky=tk.EW, pady=(8, 0))
        ttk.Label(opts, text="Style", style="Card.TLabel").grid(row=0, column=0, sticky=tk.W)
        ttk.Combobox(
            opts,
            textvariable=self._style,
            values=sorted(PRESETS.keys()),
            state="readonly",
            width=18,
        ).grid(row=0, column=1, sticky=tk.W, padx=(8, 24))

        ttk.Label(opts, text="Order", style="Card.TLabel").grid(row=0, column=2, sticky=tk.W)
        ttk.Combobox(
            opts,
            textvariable=self._sort,
            values=("name", "date"),
            state="readonly",
            width=10,
        ).grid(row=0, column=3, sticky=tk.W, padx=(8, 0))

        timing = ttk.Frame(card, style="Card.TFrame")
        timing.grid(row=7, column=0, columnspan=3, sticky=tk.EW, pady=(12, 0))
        ttk.Checkbutton(
            timing,
            text="Custom timing",
            variable=self._use_custom_timing,
            command=self._toggle_timing,
        ).grid(row=0, column=0, columnspan=4, sticky=tk.W)

        ttk.Label(timing, text="Seconds / photo", style="Card.TLabel").grid(
            row=1, column=0, sticky=tk.W, pady=(6, 0)
        )
        self._seconds_spin = ttk.Spinbox(
            timing, from_=2.0, to=20.0, increment=0.5, textvariable=self._seconds, width=8
        )
        self._seconds_spin.grid(row=1, column=1, sticky=tk.W, padx=(8, 24), pady=(6, 0))

        ttk.Label(timing, text="Crossfade (sec)", style="Card.TLabel").grid(
            row=1, column=2, sticky=tk.W, pady=(6, 0)
        )
        self._crossfade_spin = ttk.Spinbox(
            timing, from_=0.0, to=4.0, increment=0.1, textvariable=self._crossfade, width=8
        )
        self._crossfade_spin.grid(row=1, column=3, sticky=tk.W, padx=(8, 0), pady=(6, 0))
        self._toggle_timing()

        self._progress = ttk.Progressbar(outer, mode="determinate", maximum=100)
        self._progress.pack(fill=tk.X, pady=(16, 6))

        ttk.Label(outer, textvariable=self._status, style="Muted.TLabel").pack(anchor=tk.W)

        actions = ttk.Frame(outer)
        actions.pack(fill=tk.X, pady=(16, 0))
        self._generate_btn = ttk.Button(
            actions, text="Generate video", style="Accent.TButton", command=self._start_generate
        )
        self._generate_btn.pack(side=tk.LEFT)
        ttk.Button(actions, text="Open output folder", command=self._open_output_folder).pack(
            side=tk.RIGHT
        )

    def _row_path(
        self,
        parent: ttk.Frame,
        label: str,
        variable: tk.StringVar,
        command,
        row: int,
    ) -> None:
        ttk.Label(parent, text=label, style="Card.TLabel").grid(row=row, column=0, sticky=tk.W, pady=4)
        ttk.Entry(parent, textvariable=variable, width=48).grid(
            row=row, column=1, sticky=tk.EW, padx=(8, 8), pady=4
        )
        ttk.Button(parent, text="Browse…", command=command).grid(row=row, column=2, pady=4)
        parent.columnconfigure(1, weight=1)

    def _pick_images(self) -> None:
        path = filedialog.askdirectory(title="Select mall photos folder")
        if path:
            self._images_dir.set(path)
            self._refresh_photo_count()

    def _pick_music(self) -> None:
        path = filedialog.askopenfilename(
            title="Select music track",
            filetypes=[
                ("Audio", "*.mp3 *.wav *.m4a *.aac *.flac *.ogg"),
                ("All files", "*.*"),
            ],
        )
        if path:
            self._music_path.set(path)

    def _use_demo_music(self) -> None:
        path = bundled_demo_path()
        if not path.is_file():
            if not messagebox.askyesno(
                "Demo track missing",
                "No bundled demo MP3 yet. Generate one now? (~2.5 min ambient bed)",
            ):
                return
            self._generate_demo_music(silent=False)
            path = bundled_demo_path()
        if path.is_file():
            self._music_path.set(str(path))
            self._status.set("Using built-in demo ambient track.")

    def _generate_demo_music(self, silent: bool = True) -> None:
        if self._busy:
            return
        self._busy = True
        self._status.set("Generating demo music…")

        def worker() -> None:
            try:
                out = generate_mp3()
            except Exception as exc:
                self.after(0, lambda: self._on_demo_error(exc))
                return
            self.after(0, lambda: self._on_demo_ready(out, silent))

        threading.Thread(target=worker, daemon=True).start()

    def _on_demo_ready(self, path: Path, silent: bool) -> None:
        self._busy = False
        self._music_path.set(str(path))
        self._status.set(f"Demo music ready: {path.name}")
        if not silent:
            messagebox.showinfo("Demo music", f"Saved to:\n{path}")

    def _on_demo_error(self, exc: Exception) -> None:
        self._busy = False
        self._status.set("Could not generate demo music.")
        messagebox.showerror("Demo music failed", str(exc))

    def _pick_output(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Save video as",
            defaultextension=".mp4",
            filetypes=[("MP4 video", "*.mp4")],
            initialfile=Path(self._output_path.get()).name,
        )
        if path:
            self._output_path.set(path)

    def _refresh_photo_count(self) -> None:
        folder = self._images_dir.get().strip()
        if not folder:
            self._photo_count.set("")
            return
        try:
            count = len(discover_images(Path(folder), sort=self._sort.get()))
            self._photo_count.set(f"{count} photos found")
        except (FileNotFoundError, ValueError) as exc:
            self._photo_count.set(str(exc))

    def _on_style_change(self, *_args) -> None:
        preset = PRESETS.get(self._style.get(), PRESETS["proper-people"])
        self._seconds.set(preset.seconds_per_image)
        self._crossfade.set(preset.crossfade_seconds)

    def _toggle_timing(self) -> None:
        state = "normal" if self._use_custom_timing.get() else "disabled"
        self._seconds_spin.configure(state=state)
        self._crossfade_spin.configure(state=state)

    def _validate(self) -> bool:
        if not self._images_dir.get().strip():
            messagebox.showwarning("Missing folder", "Choose a folder of photos.")
            return False
        if not self._music_path.get().strip():
            messagebox.showwarning("Missing music", "Choose a music file.")
            return False
        if not self._output_path.get().strip():
            messagebox.showwarning("Missing output", "Choose where to save the video.")
            return False
        return True

    def _start_generate(self) -> None:
        if self._busy or not self._validate():
            return
        self._busy = True
        self._generate_btn.configure(state=tk.DISABLED)
        self._progress["value"] = 0
        self._status.set("Starting…")

        seconds = self._seconds.get() if self._use_custom_timing.get() else None
        crossfade = self._crossfade.get() if self._use_custom_timing.get() else None

        def worker() -> None:
            try:
                out = build_video(
                    Path(self._images_dir.get()),
                    Path(self._music_path.get()),
                    Path(self._output_path.get()),
                    style=self._style.get(),
                    sort=self._sort.get(),
                    seconds_per_image=seconds,
                    crossfade_seconds=crossfade,
                    on_progress=self._on_progress_thread,
                )
            except Exception as exc:
                self.after(0, lambda: self._on_error(exc))
                return
            self.after(0, lambda: self._on_success(out))

        threading.Thread(target=worker, daemon=True).start()

    def _on_progress_thread(self, phase: str, amount: float) -> None:
        label = PHASE_LABELS.get(phase, phase)
        pct = int(amount * 100)
        self.after(0, lambda: self._apply_progress(label, pct))

    def _apply_progress(self, label: str, pct: int) -> None:
        self._status.set(label)
        self._progress["value"] = pct

    def _on_success(self, path: Path) -> None:
        self._busy = False
        self._generate_btn.configure(state=tk.NORMAL)
        self._status.set(f"Saved to {path}")
        if messagebox.askyesno("Video ready", f"Saved:\n{path}\n\nOpen the folder now?"):
            self._open_output_folder()

    def _on_error(self, exc: Exception) -> None:
        self._busy = False
        self._generate_btn.configure(state=tk.NORMAL)
        self._status.set("Something went wrong.")
        messagebox.showerror("Export failed", str(exc))

    def _open_output_folder(self) -> None:
        target = Path(self._output_path.get()).resolve().parent
        target.mkdir(parents=True, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(target)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.run(["open", str(target)], check=False)
        else:
            subprocess.run(["xdg-open", str(target)], check=False)


def run() -> None:
    app = MallMemoryApp()
    app.mainloop()


if __name__ == "__main__":
    run()
