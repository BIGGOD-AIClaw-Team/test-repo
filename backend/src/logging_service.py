import logging
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

class StructuredLogFormatter(logging.Formatter):
    """结构化日志格式化器"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # 添加额外字段
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        # 敏感字段脱敏
        sensitive_keys = ["api_key", "token", "password", "secret", "authorization"]
        for key in sensitive_keys:
            if key in str(log_data.get("message", "")):
                log_data["message"] = "[REDACTED]"
        
        return json.dumps(log_data)

class StructuredLogger:
    """结构化日志服务"""
    
    _loggers = {}
    
    def __init__(self, name: str, level: str = None):
        self.name = name
        self.logger = logging.getLogger(name)
        
        if not self.logger.handlers:
            log_level = level or os.getenv("LOG_LEVEL", "INFO").upper()
            self.logger.setLevel(getattr(logging, log_level))
            
            # Console handler
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(StructuredLogFormatter())
            self.logger.addHandler(ch)
            
            # File handler
            log_dir = Path("./logs")
            log_dir.mkdir(exist_ok=True)
            fh = logging.FileHandler(log_dir / f"{name}_{datetime.now().date()}.jsonl")
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(StructuredLogFormatter())
            self.logger.addHandler(fh)
    
    def _log(self, level: str, event: str, **kwargs):
        extra = {"event": event, **kwargs}
        getattr(self.logger, level.lower())(event, extra=extra)
    
    def debug(self, event: str, **kwargs):
        self._log("DEBUG", event, **kwargs)
    
    def info(self, event: str, **kwargs):
        self._log("INFO", event, **kwargs)
    
    def warning(self, event: str, **kwargs):
        self._log("WARNING", event, **kwargs)
    
    def error(self, event: str, **kwargs):
        self._log("ERROR", event, **kwargs)

# 全局实例
agent_logger = StructuredLogger("agent")
api_logger = StructuredLogger("api")
skill_logger = StructuredLogger("skill")
mcp_logger = StructuredLogger("mcp")
