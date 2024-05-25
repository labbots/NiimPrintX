import tkinter as tk
from tkinter import ttk

from .CanvasOperation import CanvasOperation


class CanvasSelector:
    def __init__(self, parent, config, text_op, img_op):
        self.parent = parent
        self.config = config
        self.frame = ttk.Frame(parent)
        self.canvas_op = CanvasOperation(config, text_op, img_op)
        self.create_widgets()

    def create_widgets(self):
        device_label = tk.Label(self.frame, text="Device")
        device_label.pack(side=tk.LEFT, padx=10)
        self.selected_device = tk.StringVar(value="D110")
        device_option = ttk.Combobox(self.frame, textvariable=self.selected_device,
                                     values=list(map(lambda x: x.upper(), self.config.label_sizes.keys())),
                                     state="readonly")
        device_option.pack(side=tk.LEFT, padx=10)
        device_option.bind("<<ComboboxSelected>>", self.update_device_label_size)
        label_size_label = tk.Label(self.frame, text="Label size")
        label_size_label.pack(side=tk.LEFT, padx=10)
        self.selected_label_size = tk.StringVar()
        self.label_size_option = ttk.Combobox(self.frame, textvariable=self.selected_label_size,
                                              state="readonly")
        self.update_device_label_size()
        self.label_size_option.pack(side=tk.LEFT, padx=10)
        self.label_size_option.bind("<<ComboboxSelected>>", self.update_canvas_size)
        self.update_canvas_size()
        self.frame.pack(side=tk.LEFT)

        # print_button = tk.Button(self.frame, text="Print")
        # print_button.pack(side=tk.RIGHT, padx=10)

    def update_device_label_size(self, event=None):
        device = self.selected_device.get().lower()
        if device:
            label_sizes = list(self.config.label_sizes[device]['size'].keys())
        else:
            label_sizes = []
        self.label_size_option['values'] = label_sizes
        if label_sizes:
            self.label_size_option.current(0)
        else:
            self.selected_label_size.set('')

    def update_canvas_size(self, event=None):
        """Update the canvas size based on the selected label size."""
        self.config.device = self.selected_device.get().lower()
        self.config.current_label_size = self.selected_label_size.get()
        label_width_mm, label_height_mm = self.config.label_sizes[self.config.device]['size'][self.config.current_label_size]

        # Convert the label size to pixels
        self.bounding_box_width = self.mm_to_pixels(label_width_mm)
        self.bounding_box_height = self.mm_to_pixels(label_height_mm)

        self.print_area_width = self.bounding_box_width - self.mm_to_pixels(2)
        self.print_area_height = self.bounding_box_height - self.mm_to_pixels(4)

        # Set the new canvas dimensions with padding
        padding = 150  # 50 pixels padding on each side
        self.canvas_width = self.bounding_box_width + padding
        self.canvas_height = self.bounding_box_height + padding

        # If a canvas exists, destroy it before creating a new one
        if hasattr(self.config, "canvas") and self.config.canvas is not None:
            self.config.canvas.destroy()

        # Create a new canvas with updated dimensions
        self.config.canvas = tk.Canvas(
            self.config.frames["top_frame"], width=self.canvas_width, height=self.canvas_height,
            highlightthickness=0, bg="lightgray"
        )
        self.config.canvas.pack(padx=0, pady=0)

        # Create a centered bounding box
        x_center = self.canvas_width // 2
        y_center = self.canvas_height // 2

        self.config.bounding_box = self.config.canvas.create_rectangle(
            x_center - self.bounding_box_width // 2,
            y_center - self.bounding_box_height // 2,
            x_center + self.bounding_box_width // 2,
            y_center + self.bounding_box_height // 2,
            outline="blue",
            width=1,
            # dash=(4, 4),
            fill="white",
            tags="label_box"
        )

        self.config.print_area_box = self.config.canvas.create_rectangle(
            x_center - self.print_area_width // 2,
            y_center - self.print_area_height // 2,
            x_center + self.print_area_width // 2,
            y_center + self.print_area_height // 2,
            outline="red",
            width=1,
            dash=(4, 4),
            fill="white",
            tags="label_box"
        )

        self.config.canvas.bind("<Button-1>", self.canvas_op.canvas_click_handler)

    def mm_to_pixels(self, mm):
        inches = mm / 25.4
        return int(inches * self.config.print_dpi)
