"""
Monitoring utilities for health checks and metrics.
"""
import time
from typing import Dict, Any, Optional
from datetime import datetime
import psutil
import os

from utils.logger import get_logger

logger = get_logger(__name__)


class HealthChecker:
    """Health checker for service components."""

    @staticmethod
    def check_vector_db(vector_store) -> Dict[str, Any]:
        """
        Check vector database health.

        Args:
            vector_store: VectorStoreManager instance

        Returns:
            Dict with status and details
        """
        try:
            if not vector_store:
                return {
                    "healthy": False,
                    "error": "Vector store not initialized"
                }

            # Try to access the vector store
            # For ChromaDB, try to list collections
            # For Qdrant, try to get client info
            if hasattr(vector_store, 'db_type'):
                db_type = vector_store.db_type
                if db_type == "chromadb":
                    # Check ChromaDB
                    if hasattr(vector_store, 'collections'):
                        return {
                            "healthy": True,
                            "db_type": db_type,
                            "collections_count": len(vector_store.collections)
                        }
                elif db_type == "qdrant":
                    # Check Qdrant
                    if hasattr(vector_store, 'qdrant_client') and vector_store.qdrant_client:
                        return {
                            "healthy": True,
                            "db_type": db_type,
                            "connected": True
                        }

            # Generic check
            return {
                "healthy": True,
                "info": "Vector store initialized"
            }

        except Exception as e:
            logger.error(f"Vector DB health check failed: {str(e)}")
            return {
                "healthy": False,
                "error": str(e)
            }

    @staticmethod
    def check_llm_api(llm_manager, openai_api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Check LLM API health (OpenAI ping).

        Args:
            llm_manager: LLMManager instance
            openai_api_key: OpenAI API key

        Returns:
            Dict with status and details
        """
        try:
            if not llm_manager:
                return {
                    "healthy": False,
                    "error": "LLM manager not initialized"
                }

            # Check if OpenAI API key is available
            if openai_api_key:
                try:
                    import openai
                    # Simple validation - check if key format is valid
                    if openai_api_key.startswith('sk-'):
                        return {
                            "healthy": True,
                            "provider": "openai",
                            "api_key_configured": True
                        }
                    else:
                        return {
                            "healthy": False,
                            "provider": "openai",
                            "error": "Invalid API key format"
                        }
                except ImportError:
                    logger.warning("OpenAI package not installed")
                    return {
                        "healthy": False,
                        "error": "OpenAI package not installed"
                    }

            # Check local models
            if hasattr(llm_manager, 'local_llm_base_url') or hasattr(llm_manager, 'ollama_base_url'):
                return {
                    "healthy": True,
                    "provider": "local",
                    "info": "Local LLM available"
                }

            return {
                "healthy": False,
                "error": "No LLM provider configured"
            }

        except Exception as e:
            logger.error(f"LLM health check failed: {str(e)}")
            return {
                "healthy": False,
                "error": str(e)
            }

    @staticmethod
    def get_system_metrics() -> Dict[str, Any]:
        """
        Get system-level metrics.

        Returns:
            Dict with system metrics
        """
        try:
            process = psutil.Process()

            # CPU usage
            cpu_percent = process.cpu_percent(interval=0.1)

            # Memory usage
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024

            # Disk usage (for vector DB path)
            disk_usage = psutil.disk_usage('/')

            return {
                "cpu_percent": round(cpu_percent, 2),
                "memory_mb": round(memory_mb, 2),
                "memory_percent": round(process.memory_percent(), 2),
                "disk_total_gb": round(disk_usage.total / (1024**3), 2),
                "disk_used_gb": round(disk_usage.used / (1024**3), 2),
                "disk_free_gb": round(disk_usage.free / (1024**3), 2),
                "disk_percent": disk_usage.percent
            }

        except Exception as e:
            logger.error(f"Failed to get system metrics: {str(e)}")
            return {}


class MetricsCollector:
    """Collector for application metrics."""

    def __init__(self):
        self.start_time = time.time()
        self.total_queries = 0
        self.total_response_time = 0.0
        self.active_connections = 0
        self.error_count = 0
        self.query_times = []  # Store last 100 query times

    def record_query(self, response_time: float):
        """Record a query execution."""
        self.total_queries += 1
        self.total_response_time += response_time

        # Keep only last 100 query times for percentile calculations
        self.query_times.append(response_time)
        if len(self.query_times) > 100:
            self.query_times.pop(0)

    def record_error(self):
        """Record an error."""
        self.error_count += 1

    def increment_connections(self):
        """Increment active connections."""
        self.active_connections += 1

    def decrement_connections(self):
        """Decrement active connections."""
        self.active_connections = max(0, self.active_connections - 1)

    def get_metrics(self, vector_db_path: str) -> Dict[str, Any]:
        """
        Get all collected metrics.

        Args:
            vector_db_path: Path to vector database

        Returns:
            Dict with all metrics
        """
        uptime = time.time() - self.start_time
        avg_response_time = self.total_response_time / \
            self.total_queries if self.total_queries > 0 else 0.0

        # Calculate percentiles
        p50 = p95 = p99 = 0.0
        if self.query_times:
            sorted_times = sorted(self.query_times)
            p50 = sorted_times[int(len(sorted_times) * 0.5)]
            p95 = sorted_times[int(len(sorted_times) * 0.95)]
            p99 = sorted_times[int(len(sorted_times) * 0.99)]

        # Get vector DB size
        vector_db_size_mb = self._get_directory_size(
            vector_db_path) / (1024 * 1024)

        # Get system metrics
        system_metrics = HealthChecker.get_system_metrics()

        return {
            "total_queries": self.total_queries,
            "error_count": self.error_count,
            "error_rate": round(self.error_count / self.total_queries * 100, 2) if self.total_queries > 0 else 0.0,
            "average_response_time_ms": round(avg_response_time * 1000, 2),
            "p50_response_time_ms": round(p50 * 1000, 2),
            "p95_response_time_ms": round(p95 * 1000, 2),
            "p99_response_time_ms": round(p99 * 1000, 2),
            "active_connections": self.active_connections,
            "vector_db_size_mb": round(vector_db_size_mb, 2),
            "uptime_seconds": round(uptime, 2),
            "uptime_hours": round(uptime / 3600, 2),
            **system_metrics
        }

    def get_prometheus_format(self, vector_db_path: str) -> str:
        """
        Get metrics in Prometheus format.

        Args:
            vector_db_path: Path to vector database

        Returns:
            Metrics in Prometheus exposition format
        """
        metrics = self.get_metrics(vector_db_path)

        prometheus_lines = [
            "# HELP rag_total_queries Total number of queries processed",
            "# TYPE rag_total_queries counter",
            f"rag_total_queries {metrics['total_queries']}",
            "",
            "# HELP rag_error_count Total number of errors",
            "# TYPE rag_error_count counter",
            f"rag_error_count {metrics['error_count']}",
            "",
            "# HELP rag_error_rate Error rate percentage",
            "# TYPE rag_error_rate gauge",
            f"rag_error_rate {metrics['error_rate']}",
            "",
            "# HELP rag_response_time_seconds Average response time in seconds",
            "# TYPE rag_response_time_seconds gauge",
            f"rag_response_time_seconds {metrics['average_response_time_ms'] / 1000}",
            "",
            "# HELP rag_response_time_p50_seconds 50th percentile response time",
            "# TYPE rag_response_time_p50_seconds gauge",
            f"rag_response_time_p50_seconds {metrics['p50_response_time_ms'] / 1000}",
            "",
            "# HELP rag_response_time_p95_seconds 95th percentile response time",
            "# TYPE rag_response_time_p95_seconds gauge",
            f"rag_response_time_p95_seconds {metrics['p95_response_time_ms'] / 1000}",
            "",
            "# HELP rag_response_time_p99_seconds 99th percentile response time",
            "# TYPE rag_response_time_p99_seconds gauge",
            f"rag_response_time_p99_seconds {metrics['p99_response_time_ms'] / 1000}",
            "",
            "# HELP rag_active_connections Number of active connections",
            "# TYPE rag_active_connections gauge",
            f"rag_active_connections {metrics['active_connections']}",
            "",
            "# HELP rag_memory_usage_bytes Memory usage in bytes",
            "# TYPE rag_memory_usage_bytes gauge",
            f"rag_memory_usage_bytes {metrics.get('memory_mb', 0) * 1024 * 1024}",
            "",
            "# HELP rag_vector_db_size_bytes Vector database size in bytes",
            "# TYPE rag_vector_db_size_bytes gauge",
            f"rag_vector_db_size_bytes {metrics['vector_db_size_mb'] * 1024 * 1024}",
            "",
            "# HELP rag_uptime_seconds Service uptime in seconds",
            "# TYPE rag_uptime_seconds counter",
            f"rag_uptime_seconds {metrics['uptime_seconds']}",
            "",
        ]

        return "\n".join(prometheus_lines)

    @staticmethod
    def _get_directory_size(path: str) -> int:
        """
        Get total size of directory in bytes.

        Args:
            path: Directory path

        Returns:
            Size in bytes
        """
        total_size = 0
        try:
            if os.path.exists(path):
                for dirpath, dirnames, filenames in os.walk(path):
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        if os.path.exists(filepath):
                            total_size += os.path.getsize(filepath)
        except Exception as e:
            logger.error(f"Error calculating directory size: {str(e)}")

        return total_size


# Global metrics collector instance
metrics_collector = MetricsCollector()
