import time
import uuid
from typing import Optional, Any
from dataclasses import dataclass, field

@dataclass
class Span:
    """追踪片段"""
    span_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    parent_span_id: Optional[str] = None
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    duration: Optional[float] = None
    status: str = "running"  # running, ok, error
    input_data: dict = field(default_factory=dict)
    output_data: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
    
    def end(self, status: str = "ok", output_data: dict = None):
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.status = status
        if output_data:
            self.output_data = output_data
    
    def to_dict(self) -> dict:
        return {
            "span_id": self.span_id,
            "name": self.name,
            "parent_span_id": self.parent_span_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": int(self.duration * 1000) if self.duration else None,
            "status": self.status,
            "input": self.input_data,
            "output": self.output_data,
            "metadata": self.metadata,
        }
