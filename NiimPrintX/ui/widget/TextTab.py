import tkinter as tk
from tkinter import ttk
from tkinter import font as tk_font
import tkinter.messagebox as messagebox

from .TextOperation import TextOperation

from devtools import debug

class TextTab:
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.frame = ttk.Frame(parent)
        self.text_op = TextOperation(self, config)
        self.create_widgets()

    def create_widgets(self):

        default_bg = 'systemWindowBackgroundColor1'
        tk.Label(self.frame, text="Content", bg=default_bg).grid(row=0, column=0, sticky='w')
        self.content_entry = tk.Entry(self.frame, highlightbackground=default_bg)
        self.content_entry.grid(row=0, column=1, sticky='ew', padx=5)
        self.content_entry.insert(0, "Text")

        tk.Label(self.frame, text="Font", bg=default_bg).grid(row=1, column=0, sticky='w')
        self.font_dropdown = ttk.Combobox(self.frame, values=tk_font.families())
        self.font_dropdown.grid(row=1, column=1, sticky='ew', padx=5)
        self.font_dropdown.set("Helvetica")
        widget_name = "font_dropdown"
        self.font_dropdown.bind("<<ComboboxSelected>>",
                                lambda event, w=widget_name: self.update_text_properties(event, w))

        self.bold_var = tk.BooleanVar()
        bold_button = tk.Checkbutton(self.frame, text="Bold", variable=self.bold_var, bg=default_bg,
                                     command=self.update_text_properties)
        bold_button.grid(row=1, column=2, sticky='w')
        self.italic_var = tk.BooleanVar()
        italic_button = tk.Checkbutton(self.frame, text="Italic", variable=self.italic_var, bg=default_bg,
                                       command=self.update_text_properties)
        italic_button.grid(row=1, column=3, sticky='w')
        self.underline_var = tk.BooleanVar()
        underline_button = tk.Checkbutton(self.frame, text="Underline", variable=self.underline_var, bg=default_bg,
                                          command=self.update_text_properties)
        underline_button.grid(row=1, column=4, sticky='w')

        tk.Label(self.frame, text="Font Size", bg=default_bg).grid(row=2, column=0, sticky='w')
        self.size_var = tk.IntVar()
        self.size_var.set(12)
        self.font_size_dropdown = tk.Spinbox(self.frame, from_=4, to=100, textvariable=self.size_var,
                                             highlightbackground=default_bg, command=self.update_text_properties)
        self.font_size_dropdown.grid(row=2, column=1, sticky='ew', padx=5)

        button_frame = tk.Frame(self.frame)
        self.add_button = tk.Button(button_frame, text="Add", highlightbackground=default_bg,
                               command=self.text_op.add_text_to_canvas)
        # add_button.grid(row=3, column=1, rowspan=4, padx=5)

        self.delete_button = tk.Button(button_frame, text="Delete", highlightbackground=default_bg,
                                  command=self.text_op.delete_text)
        self.add_button.pack(side=tk.LEFT)
        self.delete_button.pack(side=tk.LEFT)
        button_frame.grid(row=3, column=1, sticky="w")

    def update_text_properties(self, event=None, widget_name=None):
        if self.config.current_selected:
            font_obj, font_props = self.get_font_properties()
            self.config.canvas.itemconfig(self.config.current_selected, font=font_obj)
            self.config.text_items[self.config.current_selected]['font'] = font_obj
            self.config.text_items[self.config.current_selected]['font_props'] = font_props
            self.text_op.update_bbox_and_handle(self.config.current_selected)

        if widget_name == "font_dropdown":
            self.bold_var.set(False)
            self.italic_var.set(False)
            self.underline_var.set(False)

    def get_font_properties(self):
        family = self.font_dropdown.get()
        size = int(self.font_size_dropdown.get())
        weight = 'bold' if self.bold_var.get() else 'normal'
        slant = 'italic' if self.italic_var.get() else 'roman'
        underline = self.underline_var.get()
        font_props = {
            "family": family,
            "size": size,
            "weight": weight,
            "slant": slant,
            "underline": underline
        }
        font_obj = tk_font.Font(family=family, size=size, weight=weight, slant=slant, underline=underline)

        return font_obj, font_props

    def get_text_operation(self):
        return self.text_op
