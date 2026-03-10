import tkinter as tk

class GraphCanvas(tk.Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(scrollregion=(0,0,2000,2000))
        self.bind("<ButtonPress-1>", self.start_pan)
        self.bind("<B1-Motion>", self.pan)

        # zoom bindings (buttons 4/5 on Linux)
        self.bind("<Button-4>", self._on_mousewheel)
        self.bind("<Button-5>", self._on_mousewheel)

        self.scan_mark_x = 0
        self.scan_mark_y = 0
        self.scale_factor = 1.0

    def start_pan(self, event):
        self.scan_mark(event.x, event.y)

    def pan(self, event):
        self.scan_dragto(event.x, event.y, gain=1)

    def _on_mousewheel(self, event):
        # determine direction & compute factor
        if event.num == 4:
            delta = 120
        elif event.num == 5:
            delta = -120
        else:
            return
        # scale by about 60% per wheel notch for faster zoom
        factor = 1.0 + (0.005 * delta)
        self.zoom(factor, event.x, event.y)

    def zoom(self, factor, x=None, y=None):
        # default to centre if coordinates not provided
        if x is None or y is None:
            x = self.winfo_width() / 2
            y = self.winfo_height() / 2
        self.scale_factor *= factor
        self.scale('all', x, y, factor, factor)
        # update scrollregion to encompass all objects
        bbox = self.bbox("all")
        if bbox:
            self.configure(scrollregion=bbox)
