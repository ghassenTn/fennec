# Fennec Admin Dashboard Example

Web-based administration interface with real-time monitoring.

## Features

- **Real-time Metrics**: Request rate, error rate, response times
- **System Monitoring**: CPU, memory, disk usage
- **Request History**: Recent requests with status and duration
- **Auto-refresh**: Dashboard updates every 2 seconds
- **Beautiful UI**: Modern, responsive design

## Installation

```bash
pip install psutil
```

## Running the Example

```bash
python server.py
```

Open http://localhost:8000/admin in your browser.

## Dashboard Sections

### Application Metrics
- Total requests
- Request rate (req/sec)
- Error rate (%)
- Average response time
- P95 response time

### System Metrics
- CPU usage (%)
- Memory usage (%)
- Disk usage (%)
- Uptime

### Recent Requests Table
- Timestamp
- HTTP method
- Endpoint
- Status code
- Duration

## Generating Test Traffic

Use these commands to generate traffic:

```bash
# Normal requests
for i in {1..10}; do curl http://localhost:8000/users/$i; done

# Create users
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "email": "alice@example.com"}'

# Slow requests
curl http://localhost:8000/slow

# Errors
curl http://localhost:8000/error
```

## Authentication

By default, authentication is disabled for the demo. To enable:

```python
admin = AdminDashboard(
    app,
    auth_required=True,
    prefix="/admin"
)
```

Then add the admin token header:

```bash
curl -H "X-Admin-Token: admin_secret" http://localhost:8000/admin
```

## Custom Authentication

Provide a custom auth check function:

```python
def check_admin(request):
    # Your custom auth logic
    user = get_user_from_session(request)
    return user and user.is_admin

admin = AdminDashboard(
    app,
    auth_required=True,
    auth_check=check_admin,
    prefix="/admin"
)
```

## API Endpoints

The dashboard exposes these API endpoints:

```bash
# Get metrics
curl http://localhost:8000/admin/api/metrics

# Get system metrics
curl http://localhost:8000/admin/api/system

# Get real-time data
curl http://localhost:8000/admin/api/realtime
```

## Integration with Monitoring

Combine with Fennec monitoring tools:

```python
from fennec.admin import AdminDashboard
from fennec.monitoring import PrometheusMetrics

app = Application()

# Add Prometheus metrics
metrics = PrometheusMetrics()
app.add_middleware(MetricsMiddleware(metrics))

# Add admin dashboard
admin = AdminDashboard(app)
```

## Customization

### Change URL Prefix

```python
admin = AdminDashboard(app, prefix="/dashboard")
```

Access at: http://localhost:8000/dashboard

### Custom Metrics

Add custom metrics to the collector:

```python
admin.metrics.record_custom_metric("cache_hits", 100)
```

## Production Deployment

### Security Recommendations

1. **Enable Authentication**: Always require auth in production
2. **Use HTTPS**: Protect admin traffic with TLS
3. **Restrict Access**: Use firewall rules or VPN
4. **Audit Logging**: Log all admin actions
5. **Rate Limiting**: Prevent abuse

### Example Production Setup

```python
admin = AdminDashboard(
    app,
    auth_required=True,
    auth_check=verify_admin_jwt,
    prefix="/admin"
)

# Add rate limiting
from fennec.middleware import RateLimiter
app.add_middleware(RateLimiter(max_requests=100, window=60))
```

## Troubleshooting

### Dashboard not loading

Check that the server is running and accessible:
```bash
curl http://localhost:8000/admin
```

### Metrics not updating

Ensure you're generating traffic to the application endpoints.

### High resource usage

The dashboard auto-refreshes every 2 seconds. Adjust the interval in the HTML if needed.

## Next Steps

- Add user management interface
- Implement log viewer
- Add configuration management
- Create custom widgets
- Export metrics to CSV
