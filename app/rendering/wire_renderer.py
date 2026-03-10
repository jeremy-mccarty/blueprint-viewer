NODE_WIDTH = 120
HEADER_HEIGHT = 20

class WireRenderer:
    def __init__(self, canvas):
        self.canvas = canvas

    def bezier_points(self, p0, p1, p2, steps=20):
        """Generate points for a quadratic Bezier curve."""
        points = []
        for t in range(steps + 1):
            t_norm = t / steps
            x = (1 - t_norm)**2 * p0[0] + 2 * (1 - t_norm) * t_norm * p1[0] + t_norm**2 * p2[0]
            y = (1 - t_norm)**2 * p0[1] + 2 * (1 - t_norm) * t_norm * p1[1] + t_norm**2 * p2[1]
            points.extend([x, y])
        return points

    def render_pin_links(self, pin, graph):
        for linked in pin.pending_links:
            # Find the target node/pin
            target_node = None
            target_pin = None
            for node in graph.nodes:
                for p in node.pins:
                    if p.pin_id == linked or f"{node.name} {p.pin_id}" == linked:
                        target_node = node
                        target_pin = p
                        break
            if target_node and target_pin:
                x1 = pin_x(pin, graph)
                y1 = pin_y(pin, graph)
                x2 = pin_x(target_pin, graph)
                y2 = pin_y(target_pin, graph)
                # Draw Bezier curves for wires
                if pin.direction == "EGPD_Output" and target_pin.direction == "EGPD_Input":
                    # Control point at midpoint x, start y
                    p1x = (x1 + x2) / 2
                    p1y = y1
                    points = self.bezier_points((x1, y1), (p1x, p1y), (x2, y2))
                    self.canvas.create_line(*points, fill="cyan", width=2, smooth=True)
                elif pin.direction == "EGPD_Input" and target_pin.direction == "EGPD_Output":
                    # Control point at midpoint x, end y
                    p1x = (x1 + x2) / 2
                    p1y = y2
                    points = self.bezier_points((x1, y1), (p1x, p1y), (x2, y2))
                    self.canvas.create_line(*points, fill="cyan", width=2, smooth=True)
                else:
                    # Straight line for same direction or other cases
                    self.canvas.create_line(x1, y1, x2, y2, fill="cyan", width=2)

def pin_x(pin, graph):
    for node in graph.nodes:
        if pin in node.pins:
            # outputs connect from the right side, inputs from the left
            return node.x + (120 if pin.direction == "EGPD_Output" else 0)
    return 0

def pin_y(pin, graph):
    for node in graph.nodes:
        if pin in node.pins:
            # only count visible pins when computing vertical offset
            visible = [p for p in node.pins if not getattr(p, 'hidden', False)]
            if pin in visible:
                idx = visible.index(pin)
            else:
                idx = node.pins.index(pin)
            return node.y + HEADER_HEIGHT + 10 + idx * 15
    return 0