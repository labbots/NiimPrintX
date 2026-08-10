"""Image import tab — load any PNG/JPEG/WebP onto the label canvas."""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from .ImageOperation import ImageOperation


class ImageTab:
    def __init__(self, parent, config, img_op: ImageOperation | None = None):
        self.parent = parent
        self.config = config
        self.frame = ttk.Frame(parent)
        self.img_op = img_op or ImageOperation(config)
        self.create_widgets()

    def get_image_operation(self):
        return self.img_op

    def create_widgets(self):
        ttk.Label(
            self.frame,
            text="Add a custom image (PNG, JPEG, WebP, GIF). Drag to move, use the handle to resize.",
        ).pack(anchor="w", padx=8, pady=8)

        btn_row = ttk.Frame(self.frame)
        btn_row.pack(fill="x", padx=8, pady=4)

        ttk.Button(btn_row, text="Browse image…", command=self.browse_image).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_row, text="Delete selected", command=self.img_op.delete_image).pack(side=tk.LEFT, padx=4)

        tip = ttk.Label(
            self.frame,
            text="Tip: for thermal printers, high-contrast black-on-white images print best.",
            foreground="#555",
        )
        tip.pack(anchor="w", padx=8, pady=4)

    def browse_image(self):
        if self.config.canvas is None:
            messagebox.showerror("Error", "Select a device and label size first.")
            return
        path = filedialog.askopenfilename(
            title="Choose image",
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg *.webp *.gif *.bmp"),
                ("All files", "*.*"),
            ],
        )
        if path:
            try:
                self.img_op.load_image(path)
                if callable(getattr(self.config, "preview_callback", None)):
                    self.config.preview_callback()
            except Exception as e:
                messagebox.showerror("Error", f"Could not load image:\n{e}")
