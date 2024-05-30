import tkinter as tk
from tkinter import ttk
from tkinter import font as tk_font
import tkinter.messagebox as messagebox

from .TextOperation import TextOperation
from ..component.FontList import fonts

from devtools import debug


class TextTab:
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.frame = ttk.Frame(parent)
        self.text_op = TextOperation(self, config)
        self.fonts = fonts()
        self.create_widgets()

    def create_widgets(self):
        if self.config.os_system == "Darwin":
            default_bg = 'systemWindowBackgroundColor1'
        elif self.config.os_system == "Linux":
            default_bg = "grey85"
        elif self.config.os_system == "Windows":
            default_bg = 'systemButtonFace'

        tk.Label(self.frame, text="Content", bg=default_bg).grid(row=0, column=0, sticky='w')
        self.content_entry = tk.Entry(self.frame, highlightbackground=default_bg)
        self.content_entry.grid(row=0, column=1, sticky='ew', padx=5)
        self.content_entry.insert(0, "Text")

        self.sample_text_label = tk.Label(self.frame, text="Sample Text", font=('Arial', 14), bg=default_bg)
        self.sample_text_label.grid(row=0, column=2, sticky='w', columnspan=3)

        tk.Label(self.frame, text="Font Family", bg=default_bg).grid(row=1, column=0, sticky='w')
        self.font_family_dropdown = ttk.Combobox(self.frame, values=list(self.fonts.keys()))
        self.font_family_dropdown.grid(row=1, column=1, sticky='ew', padx=5)
        self.font_family_dropdown.set("Arial")
        widget_name = "font_dropdown"
        self.font_family_dropdown.bind("<<ComboboxSelected>>",
                                       lambda event, w=widget_name: self.update_text_properties(event, w))
                                       # self.update_font_list)

        # tk.Label(self.frame, text="Font", bg=default_bg).grid(row=1, column=2, sticky='w')
        # self.font_dropdown = ttk.Combobox(self.frame, state="readonly")
        # self.font_dropdown.grid(row=1, column=3, sticky='ew', padx=5)
        # widget_name = "font_dropdown"
        # self.font_dropdown.bind("<<ComboboxSelected>>",
        #                         lambda event, w=widget_name: self.update_text_properties(event, w))
        self.update_font_list()

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
        self.size_var.set(16)
        self.font_size_dropdown = tk.Spinbox(self.frame, from_=4, to=100, textvariable=self.size_var,
                                             highlightbackground=default_bg, command=self.update_text_properties)
        self.font_size_dropdown.bind('<FocusOut>', self.update_text_properties)
        self.font_size_dropdown.grid(row=2, column=1, sticky='ew', padx=5)

        tk.Label(self.frame, text="Font Kerning", bg=default_bg).grid(row=3, column=0, sticky='w')
        self.kerning_var = tk.StringVar()
        self.kerning_var.set('0')
        self.font_kerning_dropdown = tk.Spinbox(self.frame, from_=0, to=20, increment=0.1, format="%.1f", textvariable=self.kerning_var,
                                             highlightbackground=default_bg, command=self.update_text_properties)
        self.font_kerning_dropdown.bind('<FocusOut>', self.update_text_properties)
        self.font_kerning_dropdown.grid(row=3, column=1, sticky='ew', padx=5)

        button_frame = tk.Frame(self.frame)
        self.add_button = tk.Button(button_frame, text="Add", highlightbackground=default_bg,
                                    command=self.text_op.add_text_to_canvas)
        # add_button.grid(row=3, column=1, rowspan=4, padx=5)

        self.delete_button = tk.Button(button_frame, text="Delete", highlightbackground=default_bg,
                                       command=self.text_op.delete_text)
        self.add_button.pack(side=tk.LEFT)
        self.delete_button.pack(side=tk.LEFT)
        button_frame.grid(row=4, column=1, sticky="w")

    def update_font_list(self, event=None):
        font_family = self.font_family_dropdown.get()
        # self.font_dropdown['values'] = list(self.fonts[font_family]["fonts"].keys())
        # self.font_dropdown.current(0)

        content = self.content_entry.get()
        label_font = tk_font.Font(family=font_family, size=14)
        self.sample_text_label.config(font=label_font,
                                      text=f"{content} in {font_family}")

    def update_text_properties(self, event=None, widget_name=None):
        font_obj, font_props = self.get_font_properties()
        content = self.content_entry.get()
        label_font = tk_font.Font(family=font_props['family'], size=14, weight=font_props['weight'],
                                  slant=font_props['slant'])
        self.sample_text_label.config(font=label_font,
                                      text=f"{content} in {font_props['family'].replace('-', ' ')}")
        if self.config.current_selected:
            # self.config.canvas.itemconfig(self.config.current_selected, font=font_obj)
            # self.config.text_items[self.config.current_selected]['font'] = font_obj
            self.config.text_items[self.config.current_selected]['font_props'] = font_props
            self.text_op.update_bbox_and_handle(self.config.current_selected)

        # if widget_name == "font_dropdown":
        #     self.bold_var.set(False)
        #     self.italic_var.set(False)
        #     self.underline_var.set(False)

    def get_font_properties(self):
        family = self.font_family_dropdown.get()
        # font = self.font_dropdown.get()
        size = int(self.font_size_dropdown.get())
        kerning = float(self.font_kerning_dropdown.get())
        weight = 'bold' if self.bold_var.get() else 'normal'
        slant = 'italic' if self.italic_var.get() else 'roman'
        underline = self.underline_var.get()
        # font_base_name = self.fonts[family]["fonts"][font]['name']

        # font_style = None
        # if weight == 'bold' and "Bold" in self.fonts[family]["fonts"][font]["variants"]:
        #     font_style = "Bold"
        #
        # if slant == 'italic':
        #     if "Italic" in self.fonts[family]["fonts"][font]["variants"]:
        #         font_style = "Italic"
        #     elif "Oblique" in self.fonts[family]["fonts"][font]["variants"]:
        #         font_style = "Oblique"
        # if weight == 'bold' and slant == 'italic':
        #     if "Bold-Italic" in self.fonts[family]["fonts"][font]["variants"]:
        #         font_style = "Bold-Italic"
        #
        # if font_style:
        #     font_name = f"{font_base_name}-{font_style}"
        # else:
        #     if self.fonts[family]["fonts"][font]["main"]:
        #         font_name = font_base_name
        #     elif "Regular" in self.fonts[family]["fonts"][font]["variants"]:
        #         font_name = f"{font_base_name}-Regular"
        #     else:
        #         font_name = f"{font_base_name}-{self.fonts[family]['fonts'][font]['variants'][0]}"

        font_props = {
            "family": family,
            # "font": font,
            "size": size,
            "kerning": kerning,
            "weight": weight,
            "slant": slant,
            "underline": underline,
            # "font_name": font_name
        }
        font_obj = tk_font.Font(family=family, size=size, weight=weight, slant=slant, underline=underline)

        return font_obj, font_props

    def get_text_operation(self):
        return self.text_op
