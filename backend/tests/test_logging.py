import pytest
import json
import sys
import os
from pathlib import Path
from io import StringIO

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.logging_service import StructuredLogger, StructuredLogFormatter


class TestStructuredLogFormatter:
    def test_format_basic(self, caplog):
        """测试基本格式化"""
        import logging
        
        formatter = StructuredLogFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        parsed = json.loads(formatted)
        
        assert "timestamp" in parsed
        assert parsed["level"] == "INFO"
        assert parsed["logger"] == "test_logger"
        assert parsed["message"] == "Test message"
    
    def test_extra_fields(self, caplog):
        """测试额外字段"""
        import logging
        
        formatter = StructuredLogFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Event happened",
            args=(),
            exc_info=None
        )
        record.extra = {"event": "user_login", "user_id": 123}
        
        formatted = formatter.format(record)
        parsed = json.loads(formatted)
        
        assert parsed["event"] == "user_login"
        assert parsed["user_id"] == 123
    
    def test_sensitive_data_redaction(self, caplog):
        """测试敏感数据脱敏"""
        import logging
        
        formatter = StructuredLogFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="api_key=secret123",
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        parsed = json.loads(formatted)
        
        assert parsed["message"] == "[REDACTED]"


class TestStructuredLogger:
    def test_logger_creation(self, tmp_path):
        """测试日志器创建"""
        # Create a unique logger name for testing
        logger = StructuredLogger(f"test_logger_{id(self)}")
        assert logger.name is not None
        assert logger.logger is not None
    
    def test_log_levels(self, capsys):
        """测试不同日志级别"""
        import logging
        import io
        
        # Create a unique logger name
        logger_name = f"test_levels_{id(self)}"
        logger = StructuredLogger(logger_name, level="DEBUG")
        
        # Capture output
        captured = io.StringIO()
        handler = logging.StreamHandler(captured)
        handler.setFormatter(StructuredLogFormatter())
        logger.logger.addHandler(handler)
        
        logger.debug("debug_event", key="debug_value")
        logger.info("info_event", key="info_value")
        logger.warning("warning_event", key="warning_value")
        logger.error("error_event", key="error_value")
        
        output = captured.getvalue()
        assert "debug_event" in output
        assert "info_event" in output
        assert "warning_event" in output
        assert "error_event" in output
        
        # Clean up
        logger.logger.removeHandler(handler)
    
    def test_event_logging(self, capsys):
        """测试事件日志"""
        import logging
        import io
        
        logger_name = f"test_event_{id(self)}"
        logger = StructuredLogger(logger_name)
        
        captured = io.StringIO()
        handler = logging.StreamHandler(captured)
        handler.setFormatter(StructuredLogFormatter())
        logger.logger.addHandler(handler)
        
        logger.info("user_action", action="login", user_id=42)
        
        output = captured.getvalue()
        parsed = json.loads(output.strip())
        
        assert parsed["event"] == "user_action"
        assert parsed["action"] == "login"
        assert parsed["user_id"] == 42
        
        # Clean up
        logger.logger.removeHandler(handler)
