import logging
import sys
from datetime import datetime
from typing import Optional
from config.settings import settings

try:
    from elasticsearch import Elasticsearch
    ELASTICSEARCH_AVAILABLE = True
except ImportError:
    ELASTICSEARCH_AVAILABLE = False


class ElasticsearchHandler(logging.Handler):
    """Custom logging handler for Elasticsearch."""

    def __init__(self, es_url: str, index_prefix: str):
        super().__init__()
        if not ELASTICSEARCH_AVAILABLE:
            logging.warning(
                "Elasticsearch not available, logs will only go to console")
            return

        try:
            self.es_client = Elasticsearch([es_url])
            self.index_prefix = index_prefix
        except Exception as e:
            logging.warning(f"Failed to connect to Elasticsearch: {e}")
            self.es_client = None

    def emit(self, record):
        """Emit a log record to Elasticsearch."""
        if not hasattr(self, 'es_client') or self.es_client is None:
            return

        try:
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'message': self.format(record),
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno,
            }

            # Add exception info if present
            if record.exc_info:
                log_entry['exception'] = self.format(record.exc_info)

            # Add extra fields if present
            if hasattr(record, 'correlation_id'):
                log_entry['correlation_id'] = record.correlation_id
            if hasattr(record, 'workspace_id'):
                log_entry['workspace_id'] = record.workspace_id
            if hasattr(record, 'model_name'):
                log_entry['model_name'] = record.model_name

            # Create index with date pattern
            index_name = f"{self.index_prefix}-{datetime.utcnow().strftime('%Y.%m.%d')}"

            self.es_client.index(index=index_name, document=log_entry)
        except Exception as e:
            # Don't let logging errors break the application
            print(f"Failed to log to Elasticsearch: {e}", file=sys.stderr)


def setup_logger(name: str = __name__, level: Optional[str] = None) -> logging.Logger:
    """
    Set up and configure logger with console and Elasticsearch handlers.

    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Set log level from settings or parameter
    log_level = level or settings.log_level
    logger.setLevel(getattr(logging, log_level.upper()))

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Console handler with formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))

    # Format: [TIMESTAMP] LEVEL - MODULE - MESSAGE
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Elasticsearch handler if URL is configured
    if settings.elasticsearch_url:
        try:
            es_handler = ElasticsearchHandler(
                es_url=settings.elasticsearch_url,
                index_prefix=settings.elasticsearch_index_prefix
            )
            es_handler.setLevel(logging.INFO)  # Only log INFO and above to ES
            es_handler.setFormatter(formatter)
            logger.addHandler(es_handler)
        except Exception as e:
            logger.warning(f"Could not set up Elasticsearch logging: {e}")

    return logger


def get_logger(name: str = __name__) -> logging.Logger:
    """
    Get or create a logger instance.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return setup_logger(name)


# Create default logger for the application
logger = get_logger("rag-chatbot-llm")
