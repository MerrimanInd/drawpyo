from dataclasses import dataclass, field
from typing import Optional, List, Tuple


@dataclass
class RawGeometry:
    x: Optional[float] = None
    y: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    relative: bool = False
    points: List[Tuple[float, float]] = field(default_factory=list)


@dataclass
class RawMxCell:
    id: str
    parent: Optional[str] = None

    value: Optional[str] = None
    style: Optional[str] = None

    is_vertex: bool = False
    is_edge: bool = False

    source: Optional[str] = None
    target: Optional[str] = None

    geometry: Optional[RawGeometry] = None
