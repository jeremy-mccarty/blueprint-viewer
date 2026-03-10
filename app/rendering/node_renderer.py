
NODE_WIDTH = 120
HEADER_HEIGHT = 20
CORNER_RADIUS = 2

from app.config import style

class NodeRenderer:
    def format_camel_case(self, text):
        import re
        return re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)

    def __init__(self, canvas):
        self.canvas = canvas

    def create_rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
        """Create a rounded rectangle on the canvas."""
        points = []
        
        # Top-left corner
        points.extend([x1 + radius, y1])
        # Add intermediate points for smoothness
        for i in range(1, 4):
            t = i / 4
            px = x1 + radius - radius * t
            py = y1 + radius - radius * (1 - t)
            points.extend([px, py])
        points.extend([x1, y1 + radius])
        
        # Bottom-left corner
        points.extend([x1, y2 - radius])
        for i in range(1, 4):
            t = i / 4
            px = x1 + radius - radius * (1 - t)
            py = y2 - radius + radius * t
            points.extend([px, py])
        points.extend([x1 + radius, y2])
        
        # Bottom-right corner
        points.extend([x2 - radius, y2])
        for i in range(1, 4):
            t = i / 4
            px = x2 - radius + radius * t
            py = y2 - radius + radius * (1 - t)
            points.extend([px, py])
        points.extend([x2, y2 - radius])
        
        # Top-right corner
        points.extend([x2, y1 + radius])
        for i in range(1, 4):
            t = i / 4
            px = x2 - radius + radius * (1 - t)
            py = y1 + radius - radius * t
            points.extend([px, py])
        points.extend([x2 - radius, y1])
        
        # Close
        points.extend([x1 + radius, y1])
        
        return self.canvas.create_polygon(points, smooth=True, **kwargs)

    def get_node_header_color(self, class_name):
        if "Event" in class_name:
            return style.NODE_HEADER_COLORS["event"]
        elif "Function" in class_name or "CallFunction" in class_name:
            return style.NODE_HEADER_COLORS["function"]
        elif "Variable" in class_name:
            return style.NODE_HEADER_COLORS["variable"]
        elif "Macro" in class_name:
            return style.NODE_HEADER_COLORS["macro"]
        else:
            return style.NODE_HEADER_COLORS["default"]

    def render_node(self, node):
        x, y = node.x, node.y

        # Format display name with spaces for CamelCase
        display_name = self.format_camel_case(node.display_name)

        # Calculate required width based on display name and pin labels
        visible_pins = [p for p in node.pins if not getattr(p, 'hidden', False)]
        pin_label_widths = []
        for pin in visible_pins:
            label = pin.name
            if pin.default_value:
                label += f" = {pin.default_value}"
            text_id = self.canvas.create_text(0, 0, text=label, anchor="w", font=(None, 8))
            bbox = self.canvas.bbox(text_id)
            width = bbox[2] - bbox[0] if bbox else 0
            pin_label_widths.append(width)
            self.canvas.delete(text_id)

        # Calculate node width: display name, pin labels, and padding
        text_id = self.canvas.create_text(0, 0, text=display_name, anchor="center")
        bbox = self.canvas.bbox(text_id)
        text_width = bbox[2] - bbox[0] if bbox else 0
        self.canvas.delete(text_id)
        max_pin_label_width = max(pin_label_widths) if pin_label_widths else 0
        node_width = max(NODE_WIDTH, text_width + 40, max_pin_label_width + 40)
        node.width = node_width  # store the calculated width

        # Calculate node height: header, padding, pins
        pin_spacing = 18
        top_padding = 12
        bottom_padding = 12
        node_height = HEADER_HEIGHT + top_padding + len(visible_pins) * pin_spacing + bottom_padding
        node.height = node_height

        # draw overall body
        self.create_rounded_rectangle(
            x, y, x + node_width, y + node_height,
            CORNER_RADIUS,
            fill=style.NODE_FILL, outline=style.NODE_OUTLINE, width=2
        )

        # header bar
        header_color = self.get_node_header_color(node.class_name)
        self.create_rounded_rectangle(
            x, y, x + node_width, y + HEADER_HEIGHT,
            CORNER_RADIUS,
            fill=header_color, outline=style.NODE_OUTLINE, width=2
        )
        self.canvas.create_text(
            x + node_width / 2, y + HEADER_HEIGHT / 2,
            text=display_name, fill=style.TEXT_COLOR
        )

        # Draw pins below header, spaced and padded inside node
        for i, pin in enumerate(visible_pins):
            pin_y = y + HEADER_HEIGHT + top_padding + i * pin_spacing
            # determine colour based on category
            if pin.category == "exec":
                pin_col = style.EXEC_PIN_COLOR
            else:
                pin_col = style.DATA_PIN_COLOR if pin.category else style.PIN_COLOR

            # position depends on direction
            if pin.direction == "EGPD_Output":
                pin_x = x + node_width - 12
                label_anchor = "e"
                label_x = pin_x - 8
            else:
                pin_x = x + 12
                label_anchor = "w"
                label_x = pin_x + 8

            # Draw pin circle
            self.canvas.create_oval(pin_x - 4, pin_y - 4, pin_x + 4, pin_y + 4,
                                    fill=pin_col, outline="")

            # Draw pin label
            label = pin.name
            if pin.default_value:
                label += f" = {pin.default_value}"
            self.canvas.create_text(
                label_x, pin_y,
                text=label,
                fill=style.TEXT_COLOR,
                anchor=label_anchor,
                font=(None, 8)
            )
