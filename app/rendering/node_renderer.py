NODE_WIDTH = 120
HEADER_HEIGHT = 20

from app.config import style

class NodeRenderer:
    def __init__(self, canvas):
        self.canvas = canvas

    def render_node(self, node):
        x, y = node.x, node.y

        # Draw pins below header (skip hidden ones)
        visible_pins = [p for p in node.pins if not getattr(p, 'hidden', False)]
        node_height = HEADER_HEIGHT + 20 + len(visible_pins) * 15

        # draw overall body
        self.canvas.create_rectangle(
            x, y, x + NODE_WIDTH, y + node_height,
            fill=style.NODE_FILL, outline=style.NODE_OUTLINE, width=2
        )

        # header bar
        self.canvas.create_rectangle(
            x, y, x + NODE_WIDTH, y + HEADER_HEIGHT,
            fill="#333", outline=style.NODE_OUTLINE, width=2
        )
        self.canvas.create_text(
            x + NODE_WIDTH / 2, y + HEADER_HEIGHT / 2,
            text=node.display_name, fill=style.TEXT_COLOR
        )

        # Draw pins below header
        for i, pin in enumerate(visible_pins):
            pin_y = y + HEADER_HEIGHT + 10 + i * 15
            # determine colour based on category
            if pin.category == "exec":
                pin_col = style.EXEC_PIN_COLOR
            else:
                pin_col = style.DATA_PIN_COLOR if pin.category else style.PIN_COLOR

            # position depends on direction
            pin_x = x + NODE_WIDTH if pin.direction == "EGPD_Output" else x
            self.canvas.create_oval(pin_x - 4, pin_y - 4, pin_x + 4, pin_y + 4,
                                    fill=pin_col, outline="")

            label = pin.name
            if pin.default_value:
                label += f" = {pin.default_value}"
            self.canvas.create_text(
                pin_x + (10 if pin.direction == "EGPD_Output" else -10),
                pin_y,
                text=label,
                fill=style.TEXT_COLOR,
                anchor="e" if pin.direction == "EGPD_Output" else "w",
                font=(None, 8)
            )
