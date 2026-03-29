import time
import uuid
from typing import Optional
from .span import Span

class TraceContext:
    """追踪上下文"""
    
    def __init__(self, trace_id: str = None):
        self.trace_id = trace_id or str(uuid.uuid4())
        self.spans: list[Span] = []
        self._current_span: Optional[Span] = None
    
    def start_span(self, name: str, parent_span_id: str = None, input_data: dict = None) -> Span:
        span = Span(
            name=name,
            parent_span_id=parent_span_id or (self._current_span.span_id if self._current_span else None),
            input_data=input_data or {},
        )
        self.spans.append(span)
        self._current_span = span
        return span
    
    def end_span(self, span: Span, status: str = "ok", output_data: dict = None):
        span.end(status=status, output_data=output_data)
        if self._current_span == span:
            self._current_span = None
    
    def get_trace(self) -> dict:
        return {
            "trace_id": self.trace_id,
            "total_spans": len(self.spans),
            "total_duration_ms": int(sum(s.duration for s in self.spans if s.duration) * 1000),
            "spans": [s.to_dict() for s in self.spans],
        }

# 全局上下文管理
_current_trace: Optional[TraceContext] = None

def get_current_trace() -> Optional[TraceContext]:
    return _current_trace

def set_current_trace(trace: TraceContext):
    global _current_trace
    _current_trace = trace
