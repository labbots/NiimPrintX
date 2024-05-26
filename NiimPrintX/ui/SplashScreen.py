import tkinter as tk


class SplashScreen(tk.Toplevel):
    def __init__(self, image_path, master, **kwargs):
        super().__init__(master, **kwargs)
        self.overrideredirect(True)  # Remove window decorations

        # Load the image
        self.image = tk.PhotoImage(file=image_path)
        label = tk.Label(self, image=self.image)
        label.pack()
        self.withdraw()
        # Center the window
        self.update_idletasks()
        width = label.winfo_reqwidth()
        height = label.winfo_reqheight()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.deiconify()
