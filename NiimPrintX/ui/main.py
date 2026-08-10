import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from .AppConfig import AppConfig
from .widget.TextTab import TextTab
from .widget.IconTab import IconTab
from .widget.ImageTab import ImageTab
from .widget.StatusBar import StatusBar
from .widget.PrintOption import PrintOption
from .widget.Preview import ThermalPreview

from NiimPrintX.ui.widget.CanvasSelector import CanvasSelector
from NiimPrintX.ui.widget.FileMenu import FileMenu

import asyncio
import threading

from loguru import logger


logger.disable('NiimPrintX.nimmy')

from devtools import debug


class LabelPrinterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('NiimPrintX')
        width = 1280
        height = 860
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.resizable(width=True, height=True)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.withdraw()
        self.thermal_preview = None

    def load_resources(self):
        self.async_loop = asyncio.new_event_loop()
        threading.Thread(target=self.start_asyncio_loop, daemon=True).start()

        self.app_config = AppConfig()
        if self.app_config.os_system == "Darwin":
            style = ttk.Style(self)
            style.theme_use('aqua')
        elif self.app_config.os_system == "Windows":
            style = ttk.Style(self)
            style.theme_use('xpnative')

        self.create_widgets()
        self.create_menu()
        self.printer = None
        self.after(800, self.show_main_window)

    def show_main_window(self):
        self.deiconify()
        self.lift()
        if self.thermal_preview:
            self.thermal_preview.refresh()

    def create_menu(self):
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)
        self.file_menu = FileMenu(self, menu_bar, self.app_config)

    def create_widgets(self):
        # Main horizontal split: editor (left) + thermal preview (right)
        body = tk.Frame(self)
        body.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        left = tk.Frame(body)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right = tk.Frame(body, width=380)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=8, pady=8)
        right.pack_propagate(False)

        self.app_config.frames["top_frame"] = tk.Frame(left)
        self.app_config.screen_dpi = int(self.app_config.frames["top_frame"].winfo_fpixels('1i'))
        self.app_config.frames["top_frame"].pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tab_control = ttk.Notebook(left)
        self.text_tab = TextTab(self.tab_control, self.app_config)
        self.icon_tab = IconTab(self.tab_control, self.app_config)
        # Share ImageOperation between IconTab and ImageTab via IconTab's instance
        icon_img_op = self.icon_tab.get_image_operation() if hasattr(self.icon_tab, "get_image_operation") else None
        self.image_tab = ImageTab(self.tab_control, self.app_config, img_op=icon_img_op)

        self.tab_control.add(self.text_tab.frame, text='Text / Emoji')
        self.tab_control.add(self.icon_tab.frame, text='Icons')
        self.tab_control.add(self.image_tab.frame, text='Image')
        self.tab_control.pack(expand=1, fill='both', side=tk.TOP)

        self.app_config.frames["bottom_frame"] = tk.Frame(left)

        img_op = self.image_tab.get_image_operation()
        self.canvas_selector = CanvasSelector(
            self.app_config.frames["bottom_frame"],
            self.app_config,
            self.text_tab.get_text_operation(),
            img_op,
        )

        self.print_option = PrintOption(self, self.app_config.frames["bottom_frame"], self.app_config)
        self.app_config.frames["bottom_frame"].pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Live thermal preview on the right
        self.thermal_preview = ThermalPreview(
            right,
            self.app_config,
            export_fn=self.print_option.export_to_png,
        )
        self.thermal_preview.pack(fill=tk.BOTH, expand=True)
        self.app_config.preview_callback = self.thermal_preview.refresh

        help_text = (
            "Workflow:\n"
            "1. Pick device (B21S / B1 / …)\n"
            "2. Choose label size\n"
            "3. Add text, emoji, icons or images\n"
            "4. Preview → Connect → Print"
        )
        ttk.Label(right, text=help_text, justify=tk.LEFT).pack(anchor="w", pady=8)

        self.app_config.frames["status_frame"] = tk.Frame(self)
        self.status_bar = StatusBar(self.app_config.frames["status_frame"], self.app_config)
        self.app_config.frames["status_frame"].pack(side=tk.BOTTOM, fill=tk.X)

    def start_asyncio_loop(self):
        asyncio.set_event_loop(self.async_loop)
        self.async_loop.run_forever()

    def on_close(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()


if __name__ == "__main__":
    try:
        app = LabelPrinterApp()
        app.load_resources()
        app.mainloop()
    except Exception as e:
        raise e
