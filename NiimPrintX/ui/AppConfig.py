import os
import appdirs
import platform
class AppConfig:
    def __init__(self):
        self.os_system = platform.system()
        self.print_dpi = 203  # DPI value for printing
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
        self.label_sizes = {
            "d110": {
                "size": {
                    "30mm x 15mm": (30, 15),
                    "40mm x 12mm": (40, 12),
                    "50mm x 14mm": (50, 14),
                    "75mm x 12mm": (75, 12),
                    "109mm x 12.5mm": (109, 12.5),
                },
                "density": 3
            },
            "d11": {
                "size": {
                    "30mm x 14mm": (30, 14),
                    "40mm x 12mm": (40, 12),
                    "50mm x 14mm": (50, 14),
                    "75mm x 12mm": (75, 12),
                    "109mm x 12.5mm": (109, 12.5),
                },
                "density": 3
            },
            "d101": {
                "size": {
                    "30mm x 14mm": (30, 14),
                    "40mm x 12mm": (40, 12),
                    "50mm x 14mm": (50, 14),
                    "75mm x 12mm": (75, 12),
                    "109mm x 12.5mm": (109, 12.5),
                },
                "density": 3
            },
            "b18": {
                "size": {
                    "40mm x 14mm": (40, 14),
                    "50mm x 14mm": (50, 14),
                    "120mm x 14mm": (120, 14),
                },
                "density": 3
            }
        }
        self.current_label_size = None
        self.frames = {}
        self.print_job = False
        self.printer_connected = False
        self.cache_dir = appdirs.user_cache_dir('NiimPrintX')


