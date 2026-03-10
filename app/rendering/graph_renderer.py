from app.rendering.node_renderer import NodeRenderer
from app.rendering.wire_renderer import WireRenderer

class GraphRenderer:
    def __init__(self, canvas):
        self.canvas = canvas
        self.node_renderer = NodeRenderer(canvas)
        self.wire_renderer = WireRenderer(canvas)

    def render_graph(self, graph):
        # clear canvas and update scroll region before drawing
        self.canvas.delete("all")

        # Set default scroll region if not set
        if not self.canvas.cget("scrollregion"):
            self.canvas.configure(scrollregion=(0, 0, 2000, 2000))

        if graph.nodes:
            # compute bounding box taking into account per-node height
            from app.rendering.node_renderer import NODE_WIDTH, HEADER_HEIGHT

            min_x = float('inf')
            min_y = float('inf')
            max_x = float('-inf')
            max_y = float('-inf')
            for node in graph.nodes:
                visible_pins = [p for p in node.pins if not getattr(p, 'hidden', False)]
                h = HEADER_HEIGHT + 20 + len(visible_pins) * 15
                min_x = min(min_x, node.x)
                min_y = min(min_y, node.y)
                max_x = max(max_x, node.x + node.width)
                max_y = max(max_y, node.y + h)
            self.canvas.configure(scrollregion=(min_x - 50, min_y - 50, max_x + 50, max_y + 50))

        for node in graph.nodes:
            self.node_renderer.render_node(node)
        for node in graph.nodes:
            for pin in node.pins:
                self.wire_renderer.render_pin_links(pin, graph)
