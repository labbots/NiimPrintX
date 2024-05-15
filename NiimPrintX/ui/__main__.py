import os
import sys
from NiimPrintX.ui.main import LabelPrinterApp

from NiimPrintX.ui.SplashScreen import SplashScreen

import ctypes
#
# def load_libraries():
#     if hasattr(sys, '_MEIPASS'):
#         base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
#         ctypes.CDLL(os.path.join(base_path, 'libharfbuzz.0.dylib'), mode=ctypes.RTLD_GLOBAL)
#         ctypes.CDLL(os.path.join(base_path, 'libpangocairo-1.0.0.dylib'), mode=ctypes.RTLD_GLOBAL)
#         os.environ['DYLD_LIBRARY_PATH'] = base_path + ':' + os.environ.get('DYLD_LIBRARY_PATH', '')

def load_libraries():
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    harfbuzz_path = os.path.join(base_path, 'libharfbuzz.0.dylib')
    pangocairo_path = os.path.join(base_path, 'libpangocairo-1.0.0.dylib')

    ctypes.CDLL(harfbuzz_path, mode=ctypes.RTLD_GLOBAL)
    ctypes.CDLL(pangocairo_path, mode=ctypes.RTLD_GLOBAL)

    os.environ['DYLD_LIBRARY_PATH'] = base_path + ':' + os.environ.get('DYLD_LIBRARY_PATH', '')

# load_libraries()

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys,'_MEIPASS'):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    else:
        base_path = os.path.realpath(".")

    return os.path.realpath(os.path.join(base_path, relative_path))

if __name__ == "__main__":
    try:
        app = LabelPrinterApp()
        image_path = resource_path('NiimPrintX/ui/assets/Niimprintx.png')
        splash = SplashScreen(image_path, app)  # Create the splash screen

        # Hide the main window initially
        # app.withdraw()
        app.load_resources()  # Start loading resources, then show the main window
        app.after(5000, splash.destroy)  # Automatically destroy the splash screen after 5 seconds
        app.after(5000, app.deiconify)
        app.mainloop()
    except Exception as e:
        print(f"Error {e}")
        raise e

