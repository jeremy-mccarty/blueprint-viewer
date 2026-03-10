CANVAS_BG = "#222"
NODE_FILL = "#444"
NODE_OUTLINE = "#aaa"
PIN_COLOR = "yellow"               # generic pin colour
EXEC_PIN_COLOR = "#ff3333"           # execution flow pins
DATA_PIN_COLOR = "#5af"           # data pins other than exec
WIRE_COLOR = "cyan"
TEXT_COLOR = "white"

# Node header colors based on type (matching Unreal Engine)
NODE_HEADER_COLORS = {
    "event": "#3C1E1E",  # dark red for events
    "function": "#1E3C5C",  # dark blue for functions
    "variable": "#1E3C1E",  # dark green for variables
    "macro": "#3C1E3C",  # dark purple for macros
    "default": "#2A2A2A"   # default darker gray
}

# Wire colors based on pin category (matching Unreal Engine)
WIRE_COLORS = {
    "exec": "#FFFFFF",  # white for execution
    "bool": "#E81828",  # red for boolean
    "int": "#0099FF",   # cyan blue for integer
    "float": "#31D843", # green for float
    "real": "#31D843", # green for real (alias of float)
    "string": "#FFB000", # orange for string
    "object": "#00CCFF", # cyan for object (matches screenshot blue)
    "struct": "#FFD700", # gold for struct
    "default": "#00CCFF"   # cyan fallback
}