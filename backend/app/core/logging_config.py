"""
Logging and monitoring configuration for production.
"""
import logging
import logging.handlers
import os
import sys
import json
from datetime import datetime
from typing import Dict, Any
from pathlib import Path


# Create logs directory
LOGS_DIR = Path("./data/logs")
LOGS_DIR.mkdir(parents=True, exist_ok=True)


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if available
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'duration'):
            log_data['duration_ms'] = record.duration
        
        return json.dumps(log_data)


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Convert log level string to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler (structured JSON for production, readable for development)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    
    # Use JSON format in production, simple format in development
    if os.getenv("ENVIRONMENT", "development") == "production":
        console_formatter = JSONFormatter()
    else:
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / 'arc_migrator.log',
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(file_handler)
    
    # Error file handler
    error_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / 'arc_migrator_errors.log',
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(error_handler)
    
    # Audit log handler (for user actions)
    audit_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / 'audit.log',
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=10
    )
    audit_handler.setLevel(logging.INFO)
    audit_handler.setFormatter(JSONFormatter())
    
    # Create audit logger
    audit_logger = logging.getLogger('audit')
    audit_logger.addHandler(audit_handler)
    audit_logger.setLevel(logging.INFO)
    
    logging.info(f"Logging configured with level: {log_level}")


def log_audit_event(
    event_type: str,
    user_id: str,
    details: Dict[str, Any],
    request_id: str = None
) -> None:
    """
    Log audit event for compliance and tracking.
    
    Args:
        event_type: Type of event (e.g., 'file_upload', 'mapping_create')
        user_id: User identifier
        details: Event details
        request_id: Optional request ID
    """
    audit_logger = logging.getLogger('audit')
    
    audit_data = {
        'event_type': event_type,
        'user_id': user_id,
        'timestamp': datetime.utcnow().isoformat(),
        'details': details
    }
    
    if request_id:
        audit_data['request_id'] = request_id
    
    audit_logger.info(json.dumps(audit_data))


class MetricsCollector:
    """
    Simple metrics collector for performance monitoring.
    """
    
    def __init__(self):
        self.metrics: Dict[str, list] = {}
        self.counters: Dict[str, int] = {}
    
    def record_duration(self, metric_name: str, duration_ms: float) -> None:
        """Record duration metric."""
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        self.metrics[metric_name].append(duration_ms)
        
        # Keep only last 1000 measurements
        if len(self.metrics[metric_name]) > 1000:
            self.metrics[metric_name] = self.metrics[metric_name][-1000:]
    
    def increment_counter(self, counter_name: str, value: int = 1) -> None:
        """Increment counter metric."""
        if counter_name not in self.counters:
            self.counters[counter_name] = 0
        self.counters[counter_name] += value
    
    def get_statistics(self, metric_name: str) -> Dict[str, float]:
        """Get statistics for a metric."""
        if metric_name not in self.metrics or not self.metrics[metric_name]:
            return {}
        
        values = self.metrics[metric_name]
        values_sorted = sorted(values)
        count = len(values)
        
        return {
            'count': count,
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / count,
            'p50': values_sorted[count // 2],
            'p95': values_sorted[int(count * 0.95)],
            'p99': values_sorted[int(count * 0.99)]
        }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics and counters."""
        return {
            'durations': {
                name: self.get_statistics(name)
                for name in self.metrics.keys()
            },
            'counters': self.counters.copy()
        }


# Global metrics collector instance
metrics_collector = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector instance."""
    return metrics_collector
