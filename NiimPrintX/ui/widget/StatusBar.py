import tkinter as tk
from tkinter import ttk


class StatusBar:
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.create_widgets()

    def create_widgets(self):
        """Create a status bar at the bottom of the tkinter application with a status message."""

        # Create a frame for the status bar at the bottom of the root window
        self.status_frame = tk.Frame(self.parent, bd=1, relief=tk.SUNKEN)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)  # Place at the bottom and fill horizontally

        # Create a canvas for the green circle
        circle_canvas = tk.Canvas(self.status_frame, width=20, height=20, bd=0, highlightthickness=0)
        circle_canvas.create_oval(4, 4, 16, 16, fill='red')  # Draw the green circle
        circle_canvas.pack(side=tk.RIGHT, padx=10, pady=5)  # Pack to the right with padding

        # Create a label for the status message
        self.status_label = tk.Label(self.status_frame, text='Not connected', fg='red', font=('Arial', 10))
        self.status_label.pack(side=tk.RIGHT, padx=5)  # Align to the right with padding

    def update_status(self, connection=True):
        """Update the status message and circle color to indicate connection."""

        if connection:
            text = "Connected"
            color = "green"
        else:
            text = "Not Connected"
            color = "red"
        # Update the status label text
        self.status_label.config(text=f'{text}', fg=f'{color}')

        # Update the circle canvas color to green
        canvas = self.status_frame.winfo_children()[0]
        canvas.create_oval(4, 4, 16, 16, fill=f'{color}')  # Change color to green
