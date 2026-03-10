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

    def render_blueprint(self):
        bp_text = self.text.get("1.0", tk.END)
        graph = parse_blueprint_text(bp_text)
        self.renderer.render_graph(graph)

    def clear_all(self):
        self.text.delete("1.0", tk.END)
        self.renderer.render_graph(BlueprintGraph())