import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from .AppConfig import AppConfig
from .widget.TextTab import TextTab
from .widget.IconTab import IconTab
from .widget.StatusBar import StatusBar
from .widget.PrintOption import PrintOption

from NiimPrintX.ui.widget.CanvasSelector import CanvasSelector
from NiimPrintX.ui.widget.FileMenu import FileMenu

from NiimPrintX.nimmy.printer import PrinterClient

import asyncio
import threading

from loguru import logger

logger.disable('nimmy')

from devtools import debug
class LabelPrinterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('NiimprintX')
        self.geometry('1100x800')  # Window size fixed as per your screenshot
        self.resizable(width=True, height=True)  # Allow window to be resizable
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.async_loop = asyncio.new_event_loop()
        threading.Thread(target=self.start_asyncio_loop, daemon=True).start()

        self.app_config = AppConfig()
        self.create_widgets()
        self.create_menu()
        self.printer = None

    def create_menu(self):
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)
        self.file_menu = FileMenu(self, menu_bar, self.app_config)


    def create_widgets(self):
        # Top frame to hold the canvas and Notebook
        self.app_config.frames["top_frame"] = tk.Frame(self)
        self.app_config.screen_dpi = int(self.app_config.frames["top_frame"].winfo_fpixels('1i'))

        self.app_config.frames["top_frame"].pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tab_control = ttk.Notebook(self)
        self.text_tab = TextTab(self.tab_control, self.app_config)
        self.icon_tab = IconTab(self.tab_control, self.app_config)

        self.tab_control.add(self.text_tab.frame, text='Text')
        self.tab_control.add(self.icon_tab.frame, text='Icon')
        self.tab_control.pack(expand=1, fill='both', side=tk.TOP)


        # Bottom frame with label size and print button
        self.app_config.frames["bottom_frame"] = tk.Frame(self)

        self.canvas_selector = CanvasSelector(self.app_config.frames["bottom_frame"], self.app_config,
                                              self.text_tab.get_text_operation(),
                                              self.icon_tab.get_image_operation())

        self.print_option = PrintOption(self,self.app_config.frames["bottom_frame"], self.app_config)

        self.app_config.frames["bottom_frame"].pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

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
    app = LabelPrinterApp()
    app.mainloop()