"""
Admin Dashboard

Web-based administration interface.
"""

import json
from typing import Optional, Callable
from fennec import Request, Response
from .metrics import MetricsCollector


class AdminDashboard:
    """Admin dashboard for Fennec applications."""
    
    def __init__(
        self,
        app,
        auth_required: bool = True,
        auth_check: Optional[Callable] = None,
        prefix: str = "/admin"
    ):
        """
        Initialize admin dashboard.
        
        Args:
            app: Fennec application instance
            auth_required: Whether authentication is required
            auth_check: Custom authentication check function
            prefix: URL prefix for admin routes
        """
        self.app = app
        self.auth_required = auth_required
        self.auth_check = auth_check
        self.prefix = prefix
        self.metrics = MetricsCollector()
        
        # Register routes
        self._register_routes()
    
    def _check_auth(self, request: Request) -> bool:
        """
        Check if request is authenticated.
        
        Args:
            request: HTTP request
            
        Returns:
            True if authenticated
        """
        if not self.auth_required:
            return True
        
        if self.auth_check:
            return self.auth_check(request)
        
        # Default: check for admin token in header
        token = request.headers.get('X-Admin-Token')
        return token == 'admin_secret'  # TODO: Use secure token
    
    def _register_routes(self):
        """Register admin dashboard routes."""
        
        async def dashboard_index(request: Request):
            """Admin dashboard index."""
            if not self._check_auth(request):
                return Response({"error": "Unauthorized"}, status_code=401)
            
            return Response(self._get_dashboard_html(), headers={"content-type": "text/html"})
        
        async def get_metrics(request: Request):
            """Get application metrics."""
            if not self._check_auth(request):
                return Response({"error": "Unauthorized"}, status_code=401)
            
            return Response(json.dumps(self.metrics.get_metrics()), headers={"content-type": "application/json"})
        
        async def get_system_metrics(request: Request):
            """Get system metrics."""
            if not self._check_auth(request):
                return Response({"error": "Unauthorized"}, status_code=401)
            
            return Response(json.dumps(self.metrics.get_system_metrics()), headers={"content-type": "application/json"})
        
        async def get_realtime_data(request: Request):
            """Get real-time data."""
            if not self._check_auth(request):
                return Response({"error": "Unauthorized"}, status_code=401)
            
            return Response(json.dumps(self.metrics.get_realtime_data()), headers={"content-type": "application/json"})
        
        # Register routes with the app's router
        self.app.router.add_route(f"{self.prefix}", dashboard_index, ["GET"])
        self.app.router.add_route(f"{self.prefix}/api/metrics", get_metrics, ["GET"])
        self.app.router.add_route(f"{self.prefix}/api/system", get_system_metrics, ["GET"])
        self.app.router.add_route(f"{self.prefix}/api/realtime", get_realtime_data, ["GET"])
    
    def _get_dashboard_html(self) -> str:
        """
        Get dashboard HTML.
        
        Returns:
            HTML string
        """
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Fennec Admin Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #1a202c;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            color: #1a202c;
            padding: 24px 32px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.07);
            position: sticky;
            top: 0;
            z-index: 100;
            border-bottom: 3px solid #667eea;
        }
        
        .header-content {
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header h1 { 
            font-size: 28px;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .header p { 
            color: #718096;
            margin-top: 4px;
            font-size: 14px;
        }
        
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: #10b981;
            color: white;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.8; }
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            background: white;
            border-radius: 50%;
            animation: blink 1.5s infinite;
        }
        
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        
        .container { 
            max-width: 1400px;
            margin: 0 auto;
            padding: 32px;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 24px;
            margin-bottom: 32px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            border: 1px solid rgba(255,255,255,0.3);
            position: relative;
            overflow: hidden;
        }
        
        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        }
        
        .card:hover {
            transform: translateY(-4px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.15);
        }
        
        .card h3 {
            font-size: 12px;
            color: #718096;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
        }
        
        .metric-value {
            font-size: 36px;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            line-height: 1.2;
        }
        
        .metric-label {
            font-size: 13px;
            color: #a0aec0;
            margin-top: 8px;
            font-weight: 500;
        }
        
        .metric-icon {
            position: absolute;
            top: 20px;
            right: 20px;
            font-size: 32px;
            opacity: 0.1;
        }
        
        .table-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 28px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            overflow-x: auto;
            border: 1px solid rgba(255,255,255,0.3);
        }
        
        .table-container h3 {
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 20px;
            color: #1a202c;
        }
        
        table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
        }
        
        th, td {
            padding: 14px 16px;
            text-align: left;
        }
        
        th {
            background: #f7fafc;
            font-weight: 600;
            color: #4a5568;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 2px solid #e2e8f0;
        }
        
        tbody tr {
            transition: all 0.2s ease;
            border-bottom: 1px solid #e2e8f0;
        }
        
        tbody tr:hover {
            background: #f7fafc;
        }
        
        tbody tr:last-child {
            border-bottom: none;
        }
        
        .status-ok { 
            color: #10b981;
            font-weight: 600;
        }
        
        .status-error { 
            color: #ef4444;
            font-weight: 600;
        }
        
        .method-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .method-GET { background: #dbeafe; color: #1e40af; }
        .method-POST { background: #d1fae5; color: #065f46; }
        .method-PUT { background: #fef3c7; color: #92400e; }
        .method-DELETE { background: #fee2e2; color: #991b1b; }
        
        .progress-bar {
            height: 10px;
            background: #e2e8f0;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 12px;
            position: relative;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.5s ease;
            border-radius: 10px;
            position: relative;
            overflow: hidden;
        }
        
        .progress-fill::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            animation: shimmer 2s infinite;
        }
        
        @keyframes shimmer {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #718096;
        }
        
        .spinner {
            border: 3px solid #e2e8f0;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 16px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @media (max-width: 768px) {
            .container { padding: 16px; }
            .grid { grid-template-columns: 1fr; gap: 16px; }
            .header { padding: 16px; }
            .header h1 { font-size: 22px; }
            .metric-value { font-size: 28px; }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div>
                <h1>🦊 Fennec Admin Dashboard</h1>
                <p>Real-time monitoring and management</p>
            </div>
            <div class="status-badge">
                <span class="status-dot"></span>
                Live
            </div>
        </div>
    </div>
    
    <div class="container">
        <div class="grid">
            <div class="card">
                <span class="metric-icon">📊</span>
                <h3>Total Requests</h3>
                <div class="metric-value" id="total-requests">0</div>
                <div class="metric-label">All time</div>
            </div>
            <div class="card">
                <span class="metric-icon">⚡</span>
                <h3>Request Rate</h3>
                <div class="metric-value" id="request-rate">0</div>
                <div class="metric-label">req/sec</div>
            </div>
            <div class="card">
                <span class="metric-icon">⚠️</span>
                <h3>Error Rate</h3>
                <div class="metric-value" id="error-rate">0%</div>
                <div class="metric-label">of total requests</div>
            </div>
            <div class="card">
                <span class="metric-icon">⏱️</span>
                <h3>Avg Response Time</h3>
                <div class="metric-value" id="avg-response">0ms</div>
                <div class="metric-label">p95: <span id="p95-response">0ms</span></div>
            </div>
        </div>
        
        <div class="grid">
            <div class="card">
                <span class="metric-icon">💻</span>
                <h3>CPU Usage</h3>
                <div class="metric-value" id="cpu-usage">0%</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="cpu-progress" style="width: 0%"></div>
                </div>
            </div>
            <div class="card">
                <span class="metric-icon">🧠</span>
                <h3>Memory Usage</h3>
                <div class="metric-value" id="memory-usage">0%</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="memory-progress" style="width: 0%"></div>
                </div>
            </div>
            <div class="card">
                <span class="metric-icon">💾</span>
                <h3>Disk Usage</h3>
                <div class="metric-value" id="disk-usage">0%</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="disk-progress" style="width: 0%"></div>
                </div>
            </div>
            <div class="card">
                <span class="metric-icon">⏰</span>
                <h3>Uptime</h3>
                <div class="metric-value" id="uptime">0s</div>
                <div class="metric-label">Since start</div>
            </div>
        </div>
        
        <div class="table-container">
            <h3>📋 Recent Requests</h3>
            <table>
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Method</th>
                        <th>Endpoint</th>
                        <th>Status</th>
                        <th>Duration</th>
                    </tr>
                </thead>
                <tbody id="recent-requests">
                    <tr><td colspan="5" class="loading"><div class="spinner"></div>Loading metrics...</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        async function fetchMetrics() {
            try {
                const response = await fetch('/admin/api/realtime');
                const data = await response.json();
                updateDashboard(data);
            } catch (error) {
                console.error('Failed to fetch metrics:', error);
            }
        }
        
        function updateDashboard(data) {
            const metrics = data.metrics;
            const system = data.system;
            
            // Update metrics with animation
            animateValue('total-requests', metrics.total_requests);
            animateValue('request-rate', metrics.request_rate.toFixed(2));
            document.getElementById('error-rate').textContent = metrics.error_rate.toFixed(1) + '%';
            document.getElementById('avg-response').textContent = metrics.avg_response_time_ms.toFixed(0) + 'ms';
            document.getElementById('p95-response').textContent = metrics.p95_response_time_ms.toFixed(0) + 'ms';
            
            // Update system metrics
            document.getElementById('cpu-usage').textContent = system.cpu_percent.toFixed(1) + '%';
            document.getElementById('cpu-progress').style.width = system.cpu_percent + '%';
            
            document.getElementById('memory-usage').textContent = system.memory_percent.toFixed(1) + '%';
            document.getElementById('memory-progress').style.width = system.memory_percent + '%';
            
            document.getElementById('disk-usage').textContent = system.disk_percent.toFixed(1) + '%';
            document.getElementById('disk-progress').style.width = system.disk_percent + '%';
            
            document.getElementById('uptime').textContent = formatUptime(metrics.uptime_seconds);
            
            // Update recent requests table
            const tbody = document.getElementById('recent-requests');
            if (metrics.recent_requests && metrics.recent_requests.length > 0) {
                tbody.innerHTML = metrics.recent_requests.map(req => `
                    <tr>
                        <td>${new Date(req.timestamp).toLocaleTimeString()}</td>
                        <td><span class="method-badge method-${req.method}">${req.method}</span></td>
                        <td>${req.endpoint}</td>
                        <td class="${req.status >= 400 ? 'status-error' : 'status-ok'}">${req.status}</td>
                        <td>${req.duration_ms}ms</td>
                    </tr>
                `).join('');
            } else {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: #a0aec0;">No requests yet</td></tr>';
            }
        }
        
        function animateValue(id, value) {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        }
        
        function formatUptime(seconds) {
            const days = Math.floor(seconds / 86400);
            const hours = Math.floor((seconds % 86400) / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            const secs = Math.floor(seconds % 60);
            
            if (days > 0) return `${days}d ${hours}h`;
            if (hours > 0) return `${hours}h ${minutes}m`;
            if (minutes > 0) return `${minutes}m ${secs}s`;
            return `${secs}s`;
        }
        
        // Initial fetch
        fetchMetrics();
        
        // Auto-refresh every 2 seconds
        setInterval(fetchMetrics, 2000);
    </script>
</body>
</html>
"""
