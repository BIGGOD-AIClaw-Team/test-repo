import pytest
import time
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.trace.span import Span
from src.trace.tracer import TraceContext, get_current_trace, set_current_trace


class TestSpan:
    def test_span_creation(self):
        """测试 Span 创建"""
        span = Span(name="test_span")
        assert span.name == "test_span"
        assert span.status == "running"
        assert span.span_id is not None
        assert len(span.span_id) == 8
    
    def test_span_end(self):
        """测试 Span 结束"""
        span = Span(name="test_span")
        time.sleep(0.01)
        span.end(status="ok", output_data={"result": "success"})
        
        assert span.status == "ok"
        assert span.end_time is not None
        assert span.duration is not None
        assert span.duration > 0
        assert span.output_data == {"result": "success"}
    
    def test_span_to_dict(self):
        """测试 Span 序列化"""
        span = Span(name="test_span", input_data={"key": "value"})
        span_dict = span.to_dict()
        
        assert "span_id" in span_dict
        assert "name" in span_dict
        assert span_dict["name"] == "test_span"
        assert span_dict["status"] == "running"
        assert span_dict["input"] == {"key": "value"}


class TestTraceContext:
    def test_trace_context_creation(self):
        """测试 TraceContext 创建"""
        trace = TraceContext()
        assert trace.trace_id is not None
        assert len(trace.spans) == 0
    
    def test_trace_context_with_id(self):
        """测试带指定 ID 的 TraceContext"""
        trace = TraceContext(trace_id="custom-id-123")
        assert trace.trace_id == "custom-id-123"
    
    def test_start_span(self):
        """测试开始 span"""
        trace = TraceContext()
        span = trace.start_span("operation1")
        
        assert span.name == "operation1"
        assert len(trace.spans) == 1
        assert trace._current_span == span
    
    def test_span_hierarchy(self):
        """测试 span 层级关系"""
        trace = TraceContext()
        span1 = trace.start_span("parent")
        span2 = trace.start_span("child")
        
        assert span2.parent_span_id == span1.span_id
    
    def test_end_span(self):
        """测试结束 span"""
        trace = TraceContext()
        span = trace.start_span("test_operation")
        trace.end_span(span, status="ok", output_data={"result": "done"})
        
        assert span.status == "ok"
        assert trace._current_span is None
    
    def test_get_trace(self):
        """测试获取追踪信息"""
        trace = TraceContext()
        span1 = trace.start_span("op1")
        trace.end_span(span1)
        span2 = trace.start_span("op2")
        trace.end_span(span2)
        
        trace_info = trace.get_trace()
        assert "trace_id" in trace_info
        assert trace_info["total_spans"] == 2
        assert "total_duration_ms" in trace_info
        assert len(trace_info["spans"]) == 2


class TestGlobalContext:
    def test_set_and_get_current_trace(self):
        """测试全局上下文管理"""
        trace = TraceContext(trace_id="global-test")
        set_current_trace(trace)
        
        retrieved = get_current_trace()
        assert retrieved is not None
        assert retrieved.trace_id == "global-test"
