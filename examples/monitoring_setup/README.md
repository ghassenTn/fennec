# Fennec Monitoring Example

Demonstrates comprehensive monitoring with Prometheus metrics, distributed tracing, and structured logging.

## Features

- **Prometheus Metrics**: HTTP requests, errors, WebSocket, database, cache
- **Distributed Tracing**: Request correlation with trace and span IDs
- **Structured Logging**: JSON-formatted logs with trace correlation
- **Health Checks**: Liveness and readiness probes for Kubernetes

## Installation

```bash
pip install prometheus-client
```

## Running the Example

```bash
python server.py
```

## Endpoints

### Monitoring Endpoints

```bash
# Prometheus metrics
curl http://localhost:8000/metrics

# Health check
curl http://localhost:8000/health

# Liveness probe
curl http://localhost:8000/health/live

# Readiness probe
curl http://localhost:8000/health/ready
```

### Test Endpoints

```bash
# Normal request
curl http://localhost:8000/users/123

# Create user
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "email": "alice@example.com"}'

# Slow request (for latency metrics)
curl http://localhost:8000/slow

# Error (for error metrics)
curl http://localhost:8000/error

# Cache metrics
curl http://localhost:8000/cache-test

# WebSocket metrics
curl http://localhost:8000/websocket-test
```

## Prometheus Metrics

Available metrics:

- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request duration histogram
- `http_requests_active` - Active requests gauge
- `http_errors_total` - Total errors
- `websocket_connections_active` - Active WebSocket connections
- `websocket_messages_total` - WebSocket messages
- `db_query_duration_seconds` - Database query duration
- `cache_hits_total` - Cache hits
- `cache_misses_total` - Cache misses

## Distributed Tracing

Each request gets a unique trace ID:

```bash
curl -v http://localhost:8000/users/123
```

Response headers:
```
X-Trace-ID: 550e8400-e29b-41d4-a716-446655440000
X-Span-ID: 12345678
```

Pass trace ID to correlate requests:
```bash
curl -H "X-Trace-ID: 550e8400-e29b-41d4-a716-446655440000" \
  http://localhost:8000/users/456
```

## Structured Logging

Logs are JSON-formatted with trace correlation:

```json
{
  "timestamp": "2024-01-04T12:00:00.000Z",
  "level": "INFO",
  "message": "GET /users/123 200",
  "logger": "demo_app",
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "span_id": "12345678",
  "http_method": "GET",
  "http_path": "/users/123",
  "http_status": 200,
  "duration_ms": 102.5
}
```

## Grafana Integration

See `grafana_dashboard.json` for a pre-built dashboard.

Import steps:
1. Open Grafana
2. Go to Dashboards → Import
3. Upload `grafana_dashboard.json`
4. Select Prometheus data source

## Prometheus Configuration

Add to `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'fennec_app'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

## Docker Compose Setup

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
  
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

Start with:
```bash
docker-compose up
```

Access:
- App: http://localhost:8000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

## Health Check Integration

### Kubernetes

```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 30

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
```

### Docker

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health/live || exit 1
```

## Best Practices

1. **Metrics**: Use histograms for latency, counters for events
2. **Tracing**: Pass trace IDs between services
3. **Logging**: Include trace context in all logs
4. **Health Checks**: Separate liveness (is running) from readiness (can serve traffic)
5. **Cardinality**: Avoid high-cardinality labels (user IDs, etc.)
