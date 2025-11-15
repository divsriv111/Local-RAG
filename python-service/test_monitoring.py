"""
Test script for monitoring and health check endpoints.

Usage:
    python test_monitoring.py [base_url]

Example:
    python test_monitoring.py http://localhost:8000
"""

import sys
import requests
import json
from typing import Dict, Any


def test_health_check(base_url: str) -> bool:
    """Test /health endpoint."""
    print("\n" + "="*50)
    print("Testing /health endpoint")
    print("="*50)

    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data.get('status')}")
            print(f"Version: {data.get('version')}")
            print("Checks:")
            for check, status in data.get('checks', {}).items():
                print(f"  - {check}: {'✓' if status else '✗'}")
            print("✅ Health check PASSED")
            return True
        else:
            print(f"❌ Health check FAILED: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Health check ERROR: {str(e)}")
        return False


def test_metrics(base_url: str) -> bool:
    """Test /metrics endpoint."""
    print("\n" + "="*50)
    print("Testing /metrics endpoint (JSON)")
    print("="*50)

    try:
        response = requests.get(f"{base_url}/metrics", timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Total Queries: {data.get('total_queries')}")
            print(
                f"Avg Response Time: {data.get('average_response_time_ms')} ms")
            print(f"Active Connections: {data.get('active_connections')}")
            print(f"Memory Usage: {data.get('memory_usage_mb')} MB")
            print(f"Vector DB Size: {data.get('vector_db_size_mb')} MB")
            print(f"Uptime: {data.get('uptime_seconds')} seconds")
            print("✅ Metrics endpoint PASSED")
            return True
        else:
            print(f"❌ Metrics endpoint FAILED: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Metrics endpoint ERROR: {str(e)}")
        return False


def test_prometheus_metrics(base_url: str) -> bool:
    """Test /metrics/prometheus endpoint."""
    print("\n" + "="*50)
    print("Testing /metrics/prometheus endpoint")
    print("="*50)

    try:
        response = requests.get(f"{base_url}/metrics/prometheus", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")

        if response.status_code == 200:
            lines = response.text.split('\n')
            metric_count = sum(
                1 for line in lines if line and not line.startswith('#'))
            print(f"Number of metrics: {metric_count}")
            print("\nSample metrics:")
            for line in lines[:20]:
                if line and not line.startswith('#'):
                    print(f"  {line}")
            print("✅ Prometheus metrics PASSED")
            return True
        else:
            print(f"❌ Prometheus metrics FAILED: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Prometheus metrics ERROR: {str(e)}")
        return False


def test_llm(base_url: str) -> bool:
    """Test /test-llm endpoint."""
    print("\n" + "="*50)
    print("Testing /test-llm endpoint")
    print("="*50)

    try:
        payload = {"model_name": "gpt-4o-mini"}
        response = requests.post(
            f"{base_url}/test-llm",
            json=payload,
            timeout=30
        )
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Model: {data.get('model_name')}")
            print(f"Success: {data.get('success')}")
            print(f"Latency: {data.get('latency_ms')} ms")
            if data.get('response'):
                print(f"Response: {data.get('response')[:50]}...")
            if data.get('error'):
                print(f"Error: {data.get('error')}")

            if data.get('success'):
                print("✅ Test LLM PASSED")
            else:
                print("⚠️  Test LLM completed but model unavailable")
            return True
        else:
            print(f"❌ Test LLM FAILED: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Test LLM ERROR: {str(e)}")
        return False


def test_models(base_url: str) -> bool:
    """Test /models endpoint."""
    print("\n" + "="*50)
    print("Testing /models endpoint")
    print("="*50)

    try:
        response = requests.get(f"{base_url}/models", timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            print(f"Available models: {len(models)}")

            for model in models:
                status_icon = "✓" if model['status'] == 'available' else "✗"
                print(
                    f"  {status_icon} {model['name']} ({model['provider']}) - {model['status']}")

            print("✅ Models endpoint PASSED")
            return True
        else:
            print(f"❌ Models endpoint FAILED: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Models endpoint ERROR: {str(e)}")
        return False


def test_correlation_id(base_url: str) -> bool:
    """Test correlation ID in headers."""
    print("\n" + "="*50)
    print("Testing Correlation ID")
    print("="*50)

    try:
        custom_id = "test-correlation-123"
        headers = {"X-Correlation-ID": custom_id}

        response = requests.get(
            f"{base_url}/health", headers=headers, timeout=10)
        returned_id = response.headers.get("X-Correlation-ID")

        print(f"Sent Correlation ID: {custom_id}")
        print(f"Returned Correlation ID: {returned_id}")

        if returned_id == custom_id:
            print("✅ Correlation ID PASSED")
            return True
        else:
            print("⚠️  Correlation ID mismatch")
            return False

    except Exception as e:
        print(f"❌ Correlation ID ERROR: {str(e)}")
        return False


def main():
    """Run all tests."""
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

    print("=" * 50)
    print("MONITORING ENDPOINTS TEST SUITE")
    print(f"Testing: {base_url}")
    print("=" * 50)

    results = {
        "Health Check": test_health_check(base_url),
        "Metrics (JSON)": test_metrics(base_url),
        "Metrics (Prometheus)": test_prometheus_metrics(base_url),
        "Test LLM": test_llm(base_url),
        "Models": test_models(base_url),
        "Correlation ID": test_correlation_id(base_url),
    }

    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)

    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")

    passed_count = sum(results.values())
    total_count = len(results)

    print("\n" + "=" * 50)
    print(f"Results: {passed_count}/{total_count} tests passed")
    print("=" * 50)

    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
