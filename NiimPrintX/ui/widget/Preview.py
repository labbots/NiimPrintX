"""Emoji picker and live 1-bit thermal preview helpers."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageOps, ImageTk


COMMON_EMOJIS = [
    "⭐", "🔥", "✅", "❌", "⚠️", "📦", "🏷️", "🔧", "💡", "🏠",
    "❤️", "💙", "💚", "💛", "💜", "🖤", "😀", "😎", "🤖", "🐱",
    "🐶", "🍕", "☕", "🍺", "🎵", "📷", "💻", "📱", "🔋", "🔌",
    "➡️", "⬅️", "⬆️", "⬇️", "➕", "➖", "✖️", "➗", "①", "②",
    "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩", "Ⓐ", "Ⓑ",
]


class EmojiPicker(tk.Toplevel):
    def __init__(self, master, on_pick):
        super().__init__(master)
        self.title("Emoji")
        self.resizable(False, False)
        self.on_pick = on_pick
        frame = ttk.Frame(self, padding=8)
        frame.pack(fill="both", expand=True)
        cols = 10
        for i, emoji in enumerate(COMMON_EMOJIS):
            btn = tk.Button(
                frame,
                text=emoji,
                font=("Noto Color Emoji", 16),
                width=3,
                command=lambda e=emoji: self._pick(e),
            )
            btn.grid(row=i // cols, column=i % cols, padx=2, pady=2)

    def _pick(self, emoji: str):
        self.on_pick(emoji)
        self.destroy()


class ThermalPreview(ttk.LabelFrame):
    """Shows a live 1-bit preview of what will be sent to the printer."""

    def __init__(self, parent, config, export_fn):
        super().__init__(parent, text="Thermal preview (1-bit)", padding=6)
        self.config = config
        self.export_fn = export_fn
        self._photo = None
        self.image_label = ttk.Label(self)
        self.image_label.pack(padx=4, pady=4)
        btn = ttk.Button(self, text="Refresh preview", command=self.refresh)
        btn.pack(pady=4)
        self.hint = ttk.Label(self, text="White paper · black heat", foreground="#666")
        self.hint.pack()

    def refresh(self):
        try:
            if self.config.canvas is None:
                self.hint.configure(text="Select a label size to preview")
                return
            # Force geometry update so export crop matches on-screen label
            self.config.canvas.update_idletasks()
            img = self.export_fn(output_filename=None)
            if img is None:
                return
            # Simulate thermal: pure B/W
            bw = ImageOps.grayscale(img.convert("RGB")).point(
                lambda p: 0 if p < 180 else 255, mode="L"
            ).convert("1")
            # Fit preview into sidebar (~340px) without distorting
            max_w, max_h = 340, 280
            scale = min(max_w / max(1, bw.width), max_h / max(1, bw.height), 3)
            scale = max(1, int(scale)) if scale >= 1 else scale
            new_size = (max(1, int(bw.width * scale)), max(1, int(bw.height * scale)))
            preview = bw.convert("L").resize(new_size, Image.Resampling.NEAREST)
            bordered = ImageOps.expand(preview, border=2, fill=0)
            self._photo = ImageTk.PhotoImage(bordered)
            self.image_label.configure(image=self._photo)
            self.hint.configure(
                text=f"{bw.width}×{bw.height}px · {(self.config.device or '?').upper()} · print area"
            )
        except Exception as e:
            self.hint.configure(text=f"Preview unavailable: {e}")
