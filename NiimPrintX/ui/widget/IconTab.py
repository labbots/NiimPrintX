import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import tkinter.messagebox as messagebox

from .ImageOperation import ImageOperation
from .TabbedIconGrid import TabbedIconGrid

class IconTab:
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.frame = ttk.Frame(parent)
        self.image_op = ImageOperation(config)
        self.create_widgets()


    def create_widgets(self):
        if self.config.os_system == "Darwin":
            default_bg = 'systemWindowBackgroundColor1'
        elif self.config.os_system == "Linux":
            default_bg = "grey85"
        elif self.config.os_system == "Windows":
            default_bg = 'systemButtonFace'
        icon_tab_frame = tk.Frame(self.frame, bg=default_bg)
        icon_tab_frame.pack(fill="both", expand=True)

        # Define a grid structure to arrange elements
        icon_tab_frame.columnconfigure(0, minsize=50, weight=0)  # For the buttons on the left
        icon_tab_frame.columnconfigure(1, weight=1)  # For the grid on the right

        # Create a frame for the buttons and stack them vertically
        button_frame = tk.Frame(icon_tab_frame, bg=default_bg, pady=50)
        button_frame.grid(row=0, column=0, sticky='ns')  # Left side, vertically stacked

        # Add the buttons to the frame
        load_image = tk.Button(button_frame, text="Add Image", width=10,
                               highlightbackground=default_bg,
                               command=self.import_image)
        delete_image = tk.Button(button_frame, text="Delete",width=10,
                                 highlightbackground=default_bg,
                                 command=self.image_op.delete_image)

        # Stack the buttons vertically
        load_image.pack(pady=5)  # Adjust padding as needed
        delete_image.pack(pady=5)

        # Create the TabbedIconGrid and align it to the right
        tabbed_icon_grid = TabbedIconGrid(
            icon_tab_frame, self.config.icon_folder,
            on_icon_selected=lambda sub_path: self.image_op.load_image(f"{self.config.icon_folder}/{sub_path}")
        )

        tabbed_icon_grid.grid(row=0, column=1, sticky='nsew', padx=10, pady=20)
        icon_tab_frame.rowconfigure(0, weight=1)


    def import_image(self):
        """Load an image into the canvas."""
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")])

        if not file_path:
            return
        self.image_op.load_image(file_path)

    def get_image_operation(self):
        return self.image_op

