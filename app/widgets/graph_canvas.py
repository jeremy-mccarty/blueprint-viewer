import tkinter as tk

class GraphCanvas(tk.Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(scrollregion=(0,0,2000,2000))
        self.bind("<ButtonPress-1>", self.on_button_press)
        self.bind("<B1-Motion>", self.on_motion)
        self.bind("<ButtonRelease-1>", self.on_button_release)

        # zoom bindings (buttons 4/5 on Linux)
        self.bind("<Button-4>", self._on_mousewheel)
        self.bind("<Button-5>", self._on_mousewheel)

        self.scan_mark_x = 0
        self.scan_mark_y = 0
        self.scale_factor = 1.0
        self.graph = None
        self.dragging_node = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0

    def set_graph(self, graph):
        self.graph = graph

    def on_button_press(self, event):
        if self.graph:
            # Convert screen coordinates to canvas coordinates
            canvas_x = self.canvasx(event.x)
            canvas_y = self.canvasy(event.y)
            # Check if clicked on a node
            for node in self.graph.nodes:
                visible_pins = [p for p in node.pins if not getattr(p, 'hidden', False)]
                node_height = 20 + 20 + len(visible_pins) * 15  # HEADER_HEIGHT + 20 + pins
                if node.x <= canvas_x <= node.x + node.width and node.y <= canvas_y <= node.y + node_height:
                    self.dragging_node = node
                    self.drag_offset_x = canvas_x - node.x
                    self.drag_offset_y = canvas_y - node.y
                    return
        # Otherwise, start panning
        self.scan_mark(event.x, event.y)

    def on_motion(self, event):
        if self.dragging_node:
            # Convert screen coordinates to canvas coordinates
            canvas_x = self.canvasx(event.x)
            canvas_y = self.canvasy(event.y)
            # Update node position
            self.dragging_node.x = canvas_x - self.drag_offset_x
            self.dragging_node.y = canvas_y - self.drag_offset_y
            # Re-render
            from app.rendering.graph_renderer import GraphRenderer
            renderer = GraphRenderer(self)
            renderer.render_graph(self.graph)
        else:
            # Pan
            self.scan_dragto(event.x, event.y, gain=1)

    def on_button_release(self, event):
        self.dragging_node = None

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
