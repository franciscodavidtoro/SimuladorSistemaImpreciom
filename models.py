
from dataclasses import dataclass, field
from typing import Dict, Any
from datetime import datetime

@dataclass
class PrintJob:
    id: str
    filename: str
    path: str
    priority: int = 0
    total_pages: int = 0
    pages_printed: int = 0
    status: str = "queued"
    timestamp_arrival: datetime = field(default_factory=datetime.now)
    printer_id: str = None
    exit_time: datetime = None
    pdf_path: str = None
    extra: Dict[str, Any] = field(default_factory=dict)
