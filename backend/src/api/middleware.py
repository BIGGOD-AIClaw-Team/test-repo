import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from ..logging_service import api_logger
from ..trace.tracer import TraceContext, set_current_trace

class TracingMiddleware(BaseHTTPMiddleware):
    """请求追踪中间件"""
    
    async def dispatch(self, request: Request, call_next):
        trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
        start_time = time.time()
        
        # 创建 Trace 上下文
        trace = TraceContext(trace_id=trace_id)
        set_current_trace(trace)
        
        # 记录请求
        api_logger.info(
            "request_start",
            method=request.method,
            path=request.url.path,
            trace_id=trace_id,
        )
        
        response = await call_next(request)
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # 记录响应
        api_logger.info(
            "request_end",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=duration_ms,
            trace_id=trace_id,
        )
        
        response.headers["X-Trace-ID"] = trace_id
        return response
