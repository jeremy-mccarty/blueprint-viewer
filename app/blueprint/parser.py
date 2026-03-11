import re
from app.blueprint.graph import BlueprintGraph, Node, Pin

# regular expressions for simple fields; pin blocks require balanced-paren handling
PIN_REGEX = r"CustomProperties Pin \((.*?)\)"  # kept for backward compatibility but not used
LINKEDTO_REGEX = r"LinkedTo=\(([^)]+)\)"


def _extract_pin_blocks(block: str) -> list[str]:
    """
    Return a list of pin definitions from a node block.

    The Blueprints format embeds parentheses in several places (e.g. NSLOCTEXT and structures),
    so a naive regex will stop at the first closing parenthesis. This helper scans for
    "CustomProperties Pin (" and then collects text until the matching closing paren at the same nesting level.
    """
    # Improved: Use explicit state tracking for balanced parentheses
    blocks = []
    start_idx = 0
    marker = "CustomProperties Pin ("
    while True:
        idx = block.find(marker, start_idx)
        if idx == -1:
            break
        pos = idx + len(marker)
        depth = 1
        i = pos
        while i < len(block) and depth > 0:
            if block[i] == "(":
                depth += 1
            elif block[i] == ")":
                depth -= 1
            i += 1
        # text between pos and i-1 is the interior of the pin tuple
        blocks.append(block[pos:i-1])
        start_idx = i
    return blocks

def debug_material_node_extraction(block, expr_class, expr_name, name_match):
    print("--- Material Node Debug ---")
    print("Block:\n", block)
    print("Extracted expr_class:", expr_class)
    print("Extracted expr_name:", expr_name)
    print("Outer name_match:", name_match.group(1) if name_match else None)
    print("--------------------------")
            
def parse_blueprint_text(text: str) -> BlueprintGraph:
    graph = BlueprintGraph()
    # Split only top-level Begin Object blocks
    node_blocks = []
    lines = text.splitlines()
    current_block = []
    depth = 0
    for line in lines:
        if line.strip().startswith("Begin Object"):
            if depth == 0:
                current_block = [line]
            depth += 1
        elif line.strip().startswith("End Object"):
            depth -= 1
            if depth == 0:
                current_block.append(line)
                node_blocks.append("\n".join(current_block))
                current_block = []
            elif depth > 0:
                current_block.append(line)
        else:
            if depth > 0:
                current_block.append(line)

    for block in node_blocks:
        # Accept BlueprintGraph nodes and Material nodes
        is_blueprint_node = "Class=/Script/BlueprintGraph.K2Node" in block
        is_material_node = re.search(r'Class=/Script/UnrealEd\.MaterialGraphNode', block) is not None
        if not (is_blueprint_node or is_material_node):
            continue

        # Node basic info
        name_match = re.search(r'Name="([^"]+)"', block)
        x_match = re.search(r'NodePosX=([-]?\d+)', block)
        y_match = re.search(r'NodePosY=([-]?\d+)', block)

        if not name_match:
            continue

        # Isolate Material node logic
        if is_material_node:
            # Extract inner MaterialExpression class and name, even if on separate lines
            expr_class = None
            expr_name = None
            found_inner = False
            for line in block.splitlines():
                if not found_inner:
                    class_match = re.search(r'Begin Object Class=/Script/Engine\.(MaterialExpression\w+)', line)
                    if class_match:
                        expr_class = class_match.group(1)
                        found_inner = True
                elif expr_class and expr_name is None:
                    name_match_inner = re.search(r'Name="([^"]+)"', line)
                    if name_match_inner:
                        expr_name = name_match_inner.group(1)
                        break
            # If not found, try MaterialExpression= line
            if not expr_class or not expr_name:
                mat_expr_match = re.search(r'MaterialExpression="/Script/Engine\.(MaterialExpression\w+)\'([^"]+)', block)
                if mat_expr_match:
                    expr_class = mat_expr_match.group(1)
                    expr_name = mat_expr_match.group(2)
            debug_material_node_extraction(block, expr_class, expr_name, name_match)
            if expr_class and expr_name:
                class_name = expr_class
                node_name = expr_name
            else:
                node_name = name_match.group(1)
                class_name = "MaterialGraphNode"
        else:
            # Use CustomFunctionName if present, otherwise Name
            custom_name_match = re.search(r'CustomFunctionName="([^"]*)"', block)
            node_name = name_match.group(1)
            if custom_name_match and custom_name_match.group(1).strip():
                node_name = custom_name_match.group(1)

            # Simplify names based on class
            class_name = ""
            class_match = re.search(r'Class=/Script/BlueprintGraph\.([^ ]+)', block)
            if class_match:
                class_name = class_match.group(1)
                if class_name == "K2Node_VariableGet":
                    node_name = "Get"
                elif class_name == "K2Node_VariableSet":
                    node_name = "Set"
                elif class_name == "K2Node_Event":
                    event_match = re.search(r'EventReference=\([^)]*MemberName="([^"]+)"', block)
                    if event_match and event_match.group(1):
                        member_name = event_match.group(1)
                        if member_name.startswith("Receive"):
                            node_name = member_name[7:]  # remove "Receive"
                        else:
                            node_name = member_name
                elif class_name == "K2Node_MacroInstance":
                    macro_match = re.search(r'MacroGraph="([^"]+)"', block)
                    if macro_match and macro_match.group(1):
                        full_path = macro_match.group(1)
                        node_name = full_path.split(':')[-1].rstrip("'")
                elif class_name == "K2Node_CallMacro":
                    macro_match = re.search(r'MacroName="([^"]+)"', block)
                    if macro_match and macro_match.group(1):
                        node_name = macro_match.group(1)
                elif class_name == "K2Node_CallFunction":
                    func_match = re.search(r'FunctionReference=\([^)]*MemberName="([^"]+)"', block)
                    if func_match and func_match.group(1):
                        node_name = func_match.group(1)
                elif class_name == "K2Node_SwitchName":
                    node_name = "Switch"
                elif class_name == "K2Node_PromotableOperator":
                    op_match = re.search(r'OperationName="([^"]+)"', block)
                    if op_match and op_match.group(1):
                        op = op_match.group(1)
                        if op == "Greater":
                            node_name = ">"
                        elif op == "Less":
                            node_name = "<"
                        elif op == "Equal":
                            node_name = "=="
                        elif op == "NotEqual":
                            node_name = "!="
                        else:
                            node_name = op
                # Fallback for other K2Node_ or K2_ prefixes
                else:
                    if node_name.startswith("K2Node_"):
                        node_name = node_name[7:]  # remove "K2Node_"
                    elif node_name.startswith("K2_"):
                        node_name = node_name[3:]  # remove "K2_"
                    # Strip trailing _number
                    if "_" in node_name and node_name.split("_")[-1].isdigit():
                        node_name = "_".join(node_name.split("_")[:-1])

            if node_name == "VSize":
                node_name = "VectorLength"
            elif node_name == "IfThenElse":
                node_name = "Branch"

        node = Node(
            name=name_match.group(1),
            display_name=node_name,
            class_name=class_name,
            x=int(x_match.group(1)) if x_match else 0,
            y=int(y_match.group(1)) if y_match else 0,
            pins=[]
        )

        # Parse pins (balanced parentheses extraction handles nested tuples)
        for pin_block in _extract_pin_blocks(block):
            pin_id_match = re.search(r"PinId=([\w\d]+)", pin_block)
            pin_name_match = re.search(r'PinName="([^"]+)"', pin_block)
            direction_match = re.search(r'Direction="([^"]+)"', pin_block)
            default_value_match = re.search(r'DefaultValue="([^"]*)"', pin_block)
            pin_category_match = re.search(r'PinType\.PinCategory="([^"]+)"', pin_block)
            hidden_match = re.search(r'bHidden=(True|False)', pin_block)

            # Material node pin direction inference
            if is_material_node:
                # If pin name is 'Output' or Direction is EGPD_Output, treat as output
                pin_name = pin_name_match.group(1) if pin_name_match else ""
                if direction_match and direction_match.group(1):
                    direction = direction_match.group(1)
                elif pin_name.lower() == "output":
                    direction = "EGPD_Output"
                else:
                    direction = "EGPD_Input"
            else:
                direction = direction_match.group(1) if direction_match else "EGPD_Input"

            pin = Pin(
                pin_id=pin_id_match.group(1) if pin_id_match else "",
                name=pin_name_match.group(1) if pin_name_match else "",
                direction=direction,
                category=pin_category_match.group(1) if pin_category_match else "",
                default_value=default_value_match.group(1) if default_value_match else "",
                hidden=(hidden_match.group(1) == "True") if hidden_match else False,
                pending_links=[]
            )

            # Robustly extract LinkedTo for wires
            linked_matches = re.findall(LINKEDTO_REGEX, pin_block)
            for lm in linked_matches:
                cleaned = lm.strip().rstrip(',')
                for part in cleaned.split(','):
                    part = part.strip()
                    if part:
                        pin.pending_links.append(part)

            node.pins.append(pin)

        graph.nodes.append(node)

    return graph