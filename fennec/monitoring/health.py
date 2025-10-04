"""
Health Check Endpoints

Provides detailed health check functionality.
"""

import time
from typing import Dict, Any, List, Callable
from enum import Enum


class HealthStatus(Enum):
    """Health check status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthCheck:
    """Health check manager."""
    
    def __init__(self, service_name: str = "fennec_app"):
        """
        Initialize health check.
        
        Args:
            service_name: Name of the service
        """
        self.service_name = service_name
        self.start_time = time.time()
        self.checks: List[Dict[str, Any]] = []
    
    def add_check(self, name: str, check_func: Callable):
        """
        Add health check.
        
        Args:
            name: Check name
            check_func: Async function that returns bool
        """
        self.checks.append({
            'name': name,
            'func': check_func
        })
    
    async def run_checks(self) -> Dict[str, Any]:
        """
        Run all health checks.
        
        Returns:
            Health check results
        """
        results = []
        overall_status = HealthStatus.HEALTHY
        
        for check in self.checks:
            try:
                start = time.time()
                is_healthy = await check['func']()
                duration = time.time() - start
                
                status = HealthStatus.HEALTHY if is_healthy else HealthStatus.UNHEALTHY
                
                results.append({
                    'name': check['name'],
                    'status': status.value,
                    'duration_ms': round(duration * 1000, 2)
                })
                
                if status == HealthStatus.UNHEALTHY:
                    overall_status = HealthStatus.UNHEALTHY
                    
            except Exception as e:
                results.append({
                    'name': check['name'],
                    'status': HealthStatus.UNHEALTHY.value,
                    'error': str(e)
                })
                overall_status = HealthStatus.UNHEALTHY
        
        uptime = time.time() - self.start_time
        
        return {
            'service': self.service_name,
            'status': overall_status.value,
            'uptime_seconds': round(uptime, 2),
            'checks': results
        }
    
    async def liveness(self) -> Dict[str, Any]:
        """
        Liveness probe (is the service running?).
        
        Returns:
            Liveness status
        """
        return {
            'service': self.service_name,
            'status': HealthStatus.HEALTHY.value,
            'uptime_seconds': round(time.time() - self.start_time, 2)
        }
    
    async def readiness(self) -> Dict[str, Any]:
        """
        Readiness probe (is the service ready to accept traffic?).
        
        Returns:
            Readiness status
        """
        return await self.run_checks()
