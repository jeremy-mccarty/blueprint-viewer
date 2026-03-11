from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Pin:
    """Represents a pin on a node."""
    pin_id: str
    name: str
    direction: str
    category: str = ""            # e.g. 'exec', 'object', 'struct', 'bool', etc.
    default_value: str = ""
    hidden: bool = False            # some pins like 'self' are marked hidden in the source
    pending_links: List[str] = field(default_factory=list)

@dataclass
class Node:
    """Represents a node in the Blueprint graph."""
    name: str
    display_name: str = ""
    class_name: str = ""
    x: int = 0
    y: int = 0
    pins: List[Pin] = field(default_factory=list)
    width: int = 120

@dataclass
class BlueprintGraph:
    """Represents the entire Blueprint graph."""
    nodes: List[Node] = field(default_factory=list)