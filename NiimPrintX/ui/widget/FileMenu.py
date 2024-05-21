import base64
import io
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog, font
import pickle
from PIL import Image, ImageTk

from devtools import debug
class FileMenu:
    def __init__(self, root, parent, config):
        self.root = root
        self.parent = parent
        self.config = config
        self.create_menu()

    def create_menu(self):
        file_menu = tk.Menu(self.parent, tearoff=0)
        self.parent.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save", command=self.save_to_file)
        file_menu.add_command(label="Open", command=self.load_from_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close)

    def on_close(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.quit()

    def save_to_file(self):
        data = {
            "device": self.config.device,
            "current_label_size": self.config.current_label_size,
            "text": {},
            "image": {}
        }
        if self.config.text_items:
            debug(self.config.text_items)
            for text_id, properties in self.config.text_items.items():
                font_image = ImageTk.getimage(properties["font_image"])
                with io.BytesIO() as buffer:
                    font_image.save(buffer, format="PNG")
                    buffer.seek(0)
                    font_img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")

                item_data = {
                    "content": properties["content"],
                    "coords": self.config.canvas.coords(text_id),
                    "font_props": properties['font_props'],
                    "font_image": font_img_str
                }
                data['text'][str(text_id)] = item_data

        if self.config.image_items:
            for image_id, properties in self.config.image_items.items():
                resized_image = ImageTk.getimage(properties["image"])
                with io.BytesIO() as buffer:
                    resized_image.save(buffer, format="PNG")
                    buffer.seek(0)
                    resize_img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")

                with io.BytesIO() as buffer:
                    properties["original_image"].save(buffer, format="PNG")
                    buffer.seek(0)
                    original_img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")

                item_data = {
                    "image": resize_img_str,
                    "original_image": original_img_str,
                    "coords": self.config.canvas.coords(image_id)
                }
                data['image'][str(image_id)] = item_data

        file_path = filedialog.asksaveasfilename(defaultextension=".niim",
                                                 filetypes=[("NIIM files", "*.niim")])
        if file_path:
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)

    def load_from_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("NIIM files", "*.niim")])
        if file_path:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)

            self.root.canvas_selector.selected_device.set(data["device"].upper())
            self.root.canvas_selector.selected_label_size.set(data["current_label_size"])
            self.config.canvas.delete("all")
            self.root.canvas_selector.update_canvas_size()
            self.config.text_items = {}
            self.config.image_items = {}

            if data["text"]:
                for text_id, item_data in data["text"].items():
                    self.load_text(item_data)

            if data["image"]:
                for image_id, item_data in data["image"].items():
                    self.load_image(item_data)

    def load_text(self, data):
        font_img_data = base64.b64decode(data["font_image"])
        font_image = Image.open(io.BytesIO(font_img_data))
        font_img_tk = ImageTk.PhotoImage(font_image)
        text_id = self.config.canvas.create_image(data['coords'][0], data['coords'][1],
                                                   image=font_img_tk, anchor="nw")
        self.config.canvas.tag_bind(text_id, "<Button-1>",
                                    lambda event, tid=text_id: self.root.text_tab.text_op.select_text(event, tid))

        self.config.text_items[text_id] = {
            "font_image": font_img_tk,
            "font_props": data["font_props"],
            "content": data["content"],
            "handle": None,
            "bbox": None
        }

    def load_image(self, data):
        original_image_data = base64.b64decode(data["original_image"])
        original_image = Image.open(io.BytesIO(original_image_data))

        image_data = base64.b64decode(data["image"])
        image = Image.open(io.BytesIO(image_data))
        img_tk = ImageTk.PhotoImage(image)
        image_id = self.config.canvas.create_image(data['coords'][0], data['coords'][1],
                                                   image=img_tk, anchor="nw")

        self.config.image_items[image_id] = {
            "image": img_tk,
            "original_image": original_image,
            "bbox": None,
            "handle": None
        }

        self.config.canvas.tag_bind(image_id, "<Button-1>",
                                    lambda event, img_id=image_id: self.root.icon_tab.image_op.select_image(event,
                                                                                                            img_id))
        self.config.canvas.tag_bind(image_id, "<Button1-Motion>",
                                    lambda e, img_id=image_id: self.root.icon_tab.image_op.move_image(e, img_id))
