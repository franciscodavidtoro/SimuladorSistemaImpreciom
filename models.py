
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class PrintJob:
    id: str
    filename: str
    path: str
    priority: int = 0
    total_pages: int = 0
    pages_printed: int = 0
    status: str = "queued"
    extra: Dict[str, Any] = field(default_factory=dict)
