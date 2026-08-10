import os
import appdirs
import platform


def _sizes(*pairs):
    return {f"{w}mm x {h}mm": (w, h) for w, h in pairs}


class AppConfig:
    def __init__(self):
        self.os_system = platform.system()
        self.screen_dpi = 72
        self.text_items = {}
        self.image_items = {}
        self.current_selected = None
        self.current_selected_image = None
        self.current_dir = os.path.dirname(os.path.realpath(__file__))
        self.icon_folder = f"{self.current_dir}/icons"
        self.canvas = None
        self.bounding_box = None
        self.device = None
        # density = default; density_max = slider ceiling (B-family uses 1–5)
        self.label_sizes = {
            "d110": {
                "size": _sizes((30, 15), (40, 12), (50, 14), (75, 12), (109, 12.5)),
                "density": 3,
                "density_max": 3,
                "print_dpi": 203,
            },
            "d11": {
                "size": _sizes((30, 14), (40, 12), (50, 14), (75, 12), (109, 12.5)),
                "density": 3,
                "density_max": 3,
                "print_dpi": 203,
            },
            "d11_h": {
                "size": _sizes((30, 14), (40, 12), (50, 14), (75, 12), (109, 12.5)),
                "density": 3,
                "density_max": 5,
                "print_dpi": 300,
            },
            "d101": {
                "size": _sizes((30, 14), (40, 12), (50, 14), (75, 12), (109, 12.5)),
                "density": 3,
                "density_max": 3,
                "print_dpi": 203,
            },
            "b18": {
                "size": _sizes((40, 14), (50, 14), (120, 14)),
                "density": 3,
                "density_max": 5,
                "print_dpi": 203,
            },
            "b1": {
                "size": _sizes((50, 30), (50, 15), (60, 40), (40, 30), (30, 15), (80, 50)),
                "density": 3,
                "density_max": 5,
                "print_dpi": 203,
            },
            "b21": {
                "size": _sizes((50, 30), (50, 15), (40, 30), (30, 15), (80, 50), (60, 40)),
                "density": 3,
                "density_max": 5,
                "print_dpi": 203,
            },
            "b21s": {
                "size": _sizes((50, 30), (50, 15), (40, 30), (30, 15), (80, 50), (60, 40)),
                "density": 3,
                "density_max": 5,
                "print_dpi": 203,
            },
        }
        self.current_label_size = None
        self.frames = {}
        self.print_job = False
        self.printer_connected = False
        self.cache_dir = appdirs.user_cache_dir("NiimPrintX")
        self.preview_callback = None
