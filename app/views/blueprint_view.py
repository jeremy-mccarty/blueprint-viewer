import tkinter as tk
from app.widgets.graph_canvas import GraphCanvas
from app.blueprint.parser import parse_blueprint_text
from app.rendering.graph_renderer import GraphRenderer
from app.blueprint.graph import BlueprintGraph

from tkinter import ttk

class BlueprintView(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        # use a monospace font and enable undo/redo
        self.text = tk.Text(self, height=10, undo=True, font=("Consolas", 10))
        self.text.pack(fill="x", padx=4, pady=4)

        self.canvas = GraphCanvas(self, bg="#222")
        self.canvas.pack(fill="both", expand=True, padx=4, pady=4)

        self.renderer = GraphRenderer(self.canvas)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=4, pady=2)

        render_btn = ttk.Button(btn_frame, text="Render", command=self.render_blueprint)
        render_btn.pack(side="left", padx=(0,4))

        clear_btn = ttk.Button(btn_frame, text="Clear", command=self.clear_all)
        clear_btn.pack(side="left")

        # Green Export PNG button, lower right
        export_btn = tk.Button(btn_frame, text="Export PNG", command=self.export_canvas_png, bg="#2ecc40", fg="white", font=("Consolas", 10, "bold"))
        export_btn.pack(side="right", padx=(4,0))
    def export_canvas_png(self):
        # Export the full graph area as a PNG using Pillow, with file/location selection and dark background
        try:
            from tkinter import filedialog, messagebox
            from app.config import style
            from PIL import Image, ImageDraw, ImageFont
            graph = self.canvas.graph
            if not graph or not graph.nodes:
                messagebox.showerror("Export PNG Error", "No graph to export.")
                return
            # Compute bounding box of all nodes
            min_x = min(node.x for node in graph.nodes)
            min_y = min(node.y for node in graph.nodes)
            max_x = max(node.x + node.width for node in graph.nodes)
            max_y = max(node.y + getattr(node, 'height', 120) for node in graph.nodes)
            padding = 20
            width = int(max_x - min_x) + 2 * padding
            height = int(max_y - min_y) + 2 * padding
            # Ask user for filename/location
            png_file = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png")],
                title="Save Canvas as PNG"
            )
            if not png_file:
                return  # User cancelled
            # Create Pillow image
            img = Image.new("RGB", (width, height), style.CANVAS_BG)
            draw = ImageDraw.Draw(img)
            # Use default font
            try:
                font = ImageFont.truetype("arial.ttf", 10)
            except:
                font = ImageFont.load_default()
            # Draw nodes
            from app.rendering.node_renderer import NodeRenderer
            from app.rendering.wire_renderer import WireRenderer
            # Helper: Pillow node renderer
            def render_node_pillow(draw, node, offset_x, offset_y):
                x = node.x - min_x + padding
                y = node.y - min_y + padding
                node_width = node.width
                node_height = getattr(node, 'height', 120)
                # Header
                header_color = NodeRenderer(None).get_node_header_color(node.class_name, node)
                draw.rectangle([x, y, x + node_width, y + 20], fill=header_color, outline=None)
                # Body
                draw.rectangle([x, y + 20, x + node_width, y + node_height], fill=style.NODE_FILL, outline=style.NODE_OUTLINE, width=2)
                # Name
                display_name = node.display_name
                if node.class_name.startswith("MaterialExpression"):
                    display_name = node.class_name[len("MaterialExpression"):]
                    if "_" in node.display_name and node.display_name.split("_")[-1].isdigit():
                        display_name = display_name.split("_")[0]
                    display_name = display_name.replace("_", " ").strip()
                display_name = NodeRenderer(None).format_camel_case(display_name)
                draw.text((x + node_width / 2, y + 10), display_name, fill=style.TEXT_COLOR, font=font, anchor="mm")
                # Pins
                visible_pins = [p for p in node.pins if not getattr(p, 'hidden', False)]
                for i, pin in enumerate(visible_pins):
                    pin_y = y + 20 + 10 + i * 15
                    pin_col = style.EXEC_PIN_COLOR if pin.category == "exec" else (style.DATA_PIN_COLOR if pin.category else style.PIN_COLOR)
                    if pin.direction == "EGPD_Output":
                        pin_x = x + node_width - 12
                        label_anchor = "ra"
                        label_x = pin_x - 8
                    else:
                        pin_x = x + 12
                        label_anchor = "la"
                        label_x = pin_x + 8
                    # Draw right-pointing arrow only for exec pins, else circle
                    if pin.category == "exec":
                        points = [
                            pin_x - 6, pin_y - 6,
                            pin_x + 6, pin_y,
                            pin_x - 6, pin_y + 6
                        ]
                        draw.polygon(points, fill=pin_col, outline=None)
                    else:
                        draw.ellipse([pin_x - 4, pin_y - 4, pin_x + 4, pin_y + 4], fill=pin_col, outline=None)
                    label = pin.name
                    if pin.default_value:
                        label += f" = {pin.default_value}"
                    draw.text((label_x, pin_y), label, fill=style.TEXT_COLOR, font=font, anchor=label_anchor)
            # Draw wires
            def render_wire_pillow(draw, pin, graph, offset_x, offset_y):
                from app.rendering.wire_renderer import pin_x, pin_y
                for linked in pin.pending_links:
                    target_node = None
                    target_pin = None
                    for node in graph.nodes:
                        for p in node.pins:
                            if p.pin_id == linked or f"{node.name} {p.pin_id}" == linked or f"{node.display_name} {p.pin_id}" == linked:
                                target_node = node
                                target_pin = p
                                break
                    if target_node and target_pin:
                        x1 = pin_x(pin, graph) - min_x + padding
                        y1 = pin_y(pin, graph) - min_y + padding
                        x2 = pin_x(target_pin, graph) - min_x + padding
                        y2 = pin_y(target_pin, graph) - min_y + padding
                        # Wire color logic: Material nodes always exec=white, others use style.WIRE_COLORS
                        if target_node.class_name.startswith("MaterialExpression"):
                            wire_color = style.WIRE_COLORS.get('exec', '#FFFFFF') if pin.category == 'exec' else style.WIRE_COLORS.get(pin.category, style.WIRE_COLORS.get('default', '#00CCFF'))
                        else:
                            wire_color = style.WIRE_COLORS.get(pin.category, style.WIRE_COLORS.get('default', '#00CCFF'))
                        dist = abs(x2 - x1) * 0.4
                        # Bezier points
                        if pin.direction == "EGPD_Output" and target_pin.direction == "EGPD_Input":
                            p1 = (x1 + dist, y1)
                            p2 = (x2 - dist, y2)
                        elif pin.direction == "EGPD_Input" and target_pin.direction == "EGPD_Output":
                            p1 = (x1 - dist, y1)
                            p2 = (x2 + dist, y2)
                        else:
                            p1 = (x1, y1)
                            p2 = (x2, y2)
                        # Approximate Bezier curve
                        bezier_points = []
                        steps = 50
                        for t in range(steps + 1):
                            t_norm = t / steps
                            bx = (1 - t_norm)**3 * x1 + 3 * (1 - t_norm)**2 * t_norm * p1[0] + 3 * (1 - t_norm) * t_norm**2 * p2[0] + t_norm**3 * x2
                            by = (1 - t_norm)**3 * y1 + 3 * (1 - t_norm)**2 * t_norm * p1[1] + 3 * (1 - t_norm) * t_norm**2 * p2[1] + t_norm**3 * y2
                            bezier_points.append((bx, by))
                        draw.line(bezier_points, fill=wire_color, width=2)
            # Draw all wires first
            for node in graph.nodes:
                for pin in node.pins:
                    render_wire_pillow(draw, pin, graph, 0, 0)
            # Draw all nodes
            for node in graph.nodes:
                render_node_pillow(draw, node, 0, 0)
            img.save(png_file, "PNG")
            messagebox.showinfo("Export PNG", f"Canvas exported as {png_file}")
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Export PNG Error", str(e))

        # Ctrl+A binding: select all text and prevent default behavior
        def _select_all(event):
            self.text.tag_add("sel", "1.0", "end")
            # move insertion mark to start so further typing replaces selection
            self.text.mark_set("insert", "1.0")
            return "break"

        self.text.bind("<Control-a>", _select_all)
        self.text.bind("<Control-A>", _select_all)

        # Undo/redo shortcuts
        self.text.bind("<Control-z>", lambda e: self.text.edit_undo() or "break")
        self.text.bind("<Control-y>", lambda e: self.text.edit_redo() or "break")

        # right-click context menu for cut/copy/paste
        self._create_context_menu()
        # right-click context menu for canvas
        self._create_canvas_context_menu()

    def _create_context_menu(self):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Undo", command=lambda: self.text.edit_undo())
        menu.add_command(label="Redo", command=lambda: self.text.edit_redo())
        menu.add_separator()
        menu.add_command(label="Cut", command=lambda: self.text.event_generate("<<Cut>>"))
        menu.add_command(label="Copy", command=lambda: self.text.event_generate("<<Copy>>"))
        menu.add_command(label="Paste", command=lambda: self.text.event_generate("<<Paste>>"))
        def show_menu(event):
            menu.tk_popup(event.x_root, event.y_root)
        self.text.bind("<Button-3>", show_menu)

    def _create_canvas_context_menu(self):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Center Nodes", command=self.center_nodes_on_canvas)
        menu.add_command(label="Zoom to 100%", command=self.zoom_to_normal)
        def show_menu(event):
            menu.tk_popup(event.x_root, event.y_root)
        self.canvas.bind("<Button-3>", show_menu)

    def zoom_to_normal(self):
        # Reset zoom to 100% and recenter canvas view
        self.canvas.scale_factor = 1.0
        self.canvas.scale('all', 0, 0, 1.0, 1.0)
        bbox = self.canvas.bbox('all')
        if bbox:
            x0, y0, x1, y1 = bbox
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            center_x = (x0 + x1) / 2
            center_y = (y0 + y1) / 2
            canvas_center_x = canvas_width / 2
            canvas_center_y = canvas_height / 2
            dx = canvas_center_x - center_x
            dy = canvas_center_y - center_y
            self.canvas.move('all', dx, dy)
        self.canvas.configure(scrollregion=bbox if bbox else self.canvas.bbox('all'))

    def center_nodes_on_canvas(self):
        graph = self.canvas.graph
        if not graph or not graph.nodes:
            return
        # Compute bounding box of all nodes
        min_x = min(node.x for node in graph.nodes)
        min_y = min(node.y for node in graph.nodes)
        max_x = max(node.x + node.width for node in graph.nodes)
        max_y = max(node.y + getattr(node, 'height', 120) for node in graph.nodes)
        nodes_width = max_x - min_x
        nodes_height = max_y - min_y
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        # Check if nodes fit in current view
        current_scale = self.canvas.scale_factor
        fits_x = nodes_width * current_scale <= canvas_width
        fits_y = nodes_height * current_scale <= canvas_height
        if not (fits_x and fits_y):
            # Calculate scale to fit all nodes
            scale_x = canvas_width / nodes_width if nodes_width > 0 else 1.0
            scale_y = canvas_height / nodes_height if nodes_height > 0 else 1.0
            scale = min(scale_x, scale_y, 1.0)  # Don't zoom above 1.0
            self.canvas.scale_factor = scale
            self.canvas.scale('all', 0, 0, scale, scale)
        else:
            scale = current_scale
        # Center canvas view
        center_x = min_x + nodes_width / 2
        center_y = min_y + nodes_height / 2
        canvas_center_x = canvas_width / 2
        canvas_center_y = canvas_height / 2
        dx = canvas_center_x - center_x * scale
        dy = canvas_center_y - center_y * scale
        self.canvas.move('all', dx, dy)
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def render_blueprint(self):
        bp_text = self.text.get("1.0", tk.END)
        graph = parse_blueprint_text(bp_text)
        self.renderer.render_graph(graph)
        self.canvas.set_graph(graph)

    def clear_all(self):
        self.text.delete("1.0", tk.END)
        graph = BlueprintGraph()
        self.renderer.render_graph(graph)
        self.canvas.set_graph(graph)